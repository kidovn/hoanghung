odoo.define('hh.pyeval', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var utils = require('web.utils');
var py = window.py;
var pyeval = require('web.pyeval');

var mypy = mypy; //KIDO custom


function sync_eval_domains_and_contexts (source) {
    var contexts = ([session.user_context] || []).concat(source.contexts);
    // see Session.eval_context in Python
    return {
        context: mypyeval('contexts', contexts),
        domain: mypyeval('domains', source.domains),
        group_by: mypyeval('groupbys', source.group_by_seq || [])
    };
}

function mypyeval (type, object, context, options) {
    options = options || {};
    context = _.extend(pyeval.context(), context || {});

    //noinspection FallthroughInSwitchStatementJS
    switch(type) {
    case 'context':
    case 'contexts':
        if (type === 'context')
            object = [object];
        return eval_contexts((options.no_user_context ? [] : [session.user_context]).concat(object), context);
    case 'domain':
    case 'domains':
        if (type === 'domain')
            object = [object];
        return eval_domains(object, context);
    case 'groupbys':
        return eval_groupbys(object, context);
    }
    throw new Error("Unknow evaluation type " + type);
}

function eval_domains (domains, evaluation_context) {
    evaluation_context = _.extend(pyeval.context(), evaluation_context || {});
    var result_domain = [];
    // Normalize only if the first domain is the array ["|"] or ["!"]
    var need_normalization = (
        domains &&
        domains.length > 0 &&
        domains[0].length === 1 &&
        (domains[0][0] === "|" || domains[0][0] === "!")
    );
    _(domains).each(function (domain) {
        if (_.isString(domain)) {
            // wrap raw strings in domain
            domain = { __ref: 'domain', __debug: domain };
        }
        var domain_array_to_combine;
        switch(domain.__ref) {
        case 'domain':
            evaluation_context.context = evaluation_context;
            domain_array_to_combine = myeval(domain.__debug, wrap_context(evaluation_context));
            break;
        case 'compound_domain':
            var eval_context = eval_contexts([domain.__eval_context]);
            domain_array_to_combine = eval_domains(
                domain.__domains, _.extend({}, evaluation_context, eval_context)
            );
            break;
        default:
            domain_array_to_combine = domain;
        }
        if (need_normalization) {
            domain_array_to_combine = get_normalized_domain(domain_array_to_combine);
        }
        result_domain.push.apply(result_domain, domain_array_to_combine);
    });
    return result_domain;
}

function eval_contexts (contexts, evaluation_context) {
    evaluation_context = _.extend(pyeval.context(), evaluation_context || {});
    return _(contexts).reduce(function (result_context, ctx) {
        // __eval_context evaluations can lead to some of `contexts`'s
        // values being null, skip them as well as empty contexts
        if (_.isEmpty(ctx)) { return result_context; }
        if (_.isString(ctx)) {
            // wrap raw strings in context
            ctx = { __ref: 'context', __debug: ctx };
        }
        var evaluated = ctx;
        switch(ctx.__ref) {
        case 'context':
            evaluation_context.context = evaluation_context;
            evaluated = py.eval(ctx.__debug, wrap_context(evaluation_context));
            break;
        case 'compound_context':
            var eval_context = eval_contexts([ctx.__eval_context]);
            evaluated = eval_contexts(
                ctx.__contexts, _.extend({}, evaluation_context, eval_context));
            break;
        }
        // add newly evaluated context to evaluation context for following
        // siblings
        _.extend(evaluation_context, evaluated);
        return _.extend(result_context, evaluated);
    }, {});
}

function wrap_context (context) {
    for (var k in context) {
        if (!context.hasOwnProperty(k)) { continue; }
        var val = context[k];

        if (val === null) { continue; }
        if (val.constructor === Array) {
            context[k] = wrapping_list.fromJSON(val);
        } else if (val.constructor === Object
                   && !py.PY_isInstance(val, py.object)) {
            context[k] = wrapping_dict.fromJSON(val);
        }
    }
    return context;
}

var wrapping_dict = py.type('wrapping_dict', null, {
    __init__: function () {
        this._store = {};
    },
    __getitem__: function (key) {
        var k = key.toJSON();
        if (!(k in this._store)) {
            throw new Error("KeyError: '" + k + "'");
        }
        return wrap(this._store[k]);
    },
    __getattr__: function (key) {
        return this.__getitem__(py.str.fromJSON(key));
    },
    __len__: function () {
        return Object.keys(this._store).length
    },
    __nonzero__: function () {
        return py.PY_size(this) > 0 ? py.True : py.False;
    },
    get: function () {
        var args = py.PY_parseArgs(arguments, ['k', ['d', py.None]]);

        if (!(args.k.toJSON() in this._store)) { return args.d; }
        return this.__getitem__(args.k);
    },
    fromJSON: function (d) {
        var instance = py.PY_call(wrapping_dict);
        instance._store = d;
        return instance;
    },
    toJSON: function () {
        return this._store;
    },
});

function eval_groupbys (contexts, evaluation_context) {
    evaluation_context = _.extend(pyeval.context(), evaluation_context || {});
    var result_group = [];
    _(contexts).each(function (ctx) {
        if (_.isString(ctx)) {
            // wrap raw strings in context
            ctx = { __ref: 'context', __debug: ctx };
        }
        var group;
        var evaluated = ctx;
        switch(ctx.__ref) {
        case 'context':
            evaluation_context.context = evaluation_context;
            evaluated = py.eval(ctx.__debug, wrap_context(evaluation_context));
            break;
        case 'compound_context':
            var eval_context = eval_contexts([ctx.__eval_context]);
            evaluated = eval_contexts(
                ctx.__contexts, _.extend({}, evaluation_context, eval_context));
            break;
        }
        group = evaluated.group_by;
        if (!group) { return; }
        if (typeof group === 'string') {
            result_group.push(group);
        } else if (group instanceof Array) {
            result_group.push.apply(result_group, group);
        } else {
            throw new Error('Got invalid groupby {{'
                    + JSON.stringify(group) + '}}');
        }
        _.extend(evaluation_context, evaluated);
    });
    return result_group;
}


//mypy
function myeval(str, context) {
    return evaluate(
        py.parse(
            py.tokenize(
                str)),
        context).toJSON();
}


function evaluate(expr, context) {
    context = context || {};
    switch (expr.id) {
    case '(name)':
        var val = context[expr.value];
        if (val === undefined && expr.value in PY_builtins) {
            return PY_builtins[expr.value];
        }
        return PY_ensurepy(val, expr.value);
    case '(string)':
        return py.str.fromJSON(PY_decode_string_literal(
            expr.value, expr.unicode));
    case '(number)':
        return py.float.fromJSON(expr.value);
    case '(constant)':
        switch (expr.value) {
        case 'None': return py.None;
        case 'False': return py.False;
        case 'True': return py.True;
        }
        throw new Error("SyntaxError: unknown constant '" + expr.value + "'");
    case '(comparator)':
        var result, left = evaluate(expr.expressions[0], context);
        for(var i=0; i<expr.operators.length; ++i) {
            result = evaluate_operator(
                expr.operators[i],
                left,
                left = evaluate(expr.expressions[i+1], context));
            if (py.PY_not(result)) { return py.False; }
        }
        return py.True;
    case 'not':
        return py.PY_isTrue(evaluate(expr.first, context)) ? py.False : py.True;
    case 'and':
        var and_first = py.evaluate(expr.first, context);
        if (py.PY_isTrue(and_first.__nonzero__())) {
            return evaluate(expr.second, context);
        }
        return and_first;
    case 'or':
        var or_first = evaluate(expr.first, context);
        if (py.PY_isTrue(or_first.__nonzero__())) {
            return or_first
        }
        return evaluate(expr.second, context);
    case '(':
        if (expr.second) {
            if(expr.first.first.value == 'time'){
                console.log('expr.second[0].value ' + expr.second[0].value);
                console.log(expr.first.first.value + "." + expr.first.second.value + '("'+ expr.second[0].value+'")');
                return expr.first.first.value + "." + expr.first.second.value + '("'+ expr.second[0].value+'")';
            }
            var callable = evaluate(expr.first, context);
            var args = [], kwargs = {};
            for (var jj=0; jj<expr.second.length; ++jj) {
                var arg = expr.second[jj];
                if (arg.id !== '=') {
                    // arg
                    args.push(evaluate(arg, context));
                } else {
                    // kwarg
                    kwargs[arg.first.value] =
                        evaluate(arg.second, context);
                }
            }
            return py.PY_call(callable, args, kwargs);
        }
        var tuple_exprs = expr.first,
            tuple_values = [];
        for (var j=0, len=tuple_exprs.length; j<len; ++j) {
            tuple_values.push(evaluate(
                tuple_exprs[j], context));
        }
        return py.tuple.fromJSON(tuple_values);
    case '[':
        if (expr.second) {
            return py.PY_getItem(
                evaluate(expr.first, context),
                evaluate(expr.second, context));
        }
        var list_exprs = expr.first, list_values = [];
        for (var k=0; k<list_exprs.length; ++k) {
            list_values.push(evaluate(
                list_exprs[k], context));
        }
        return py.list.fromJSON(list_values);
    case '{':
        var dict_exprs = expr.first, dict = py.PY_call(py.dict);
        for(var l=0; l<dict_exprs.length; ++l) {
            py.PY_setItem(dict,
                evaluate(dict_exprs[l][0], context),
                evaluate(dict_exprs[l][1], context));
        }
        return dict;
    case '.':
        if (expr.second.id !== '(name)') {
            throw new Error('SyntaxError: ' + expr);
        }
        return py.PY_getAttr(evaluate(expr.first, context),
                             expr.second.value);
    // numerical operators
    case '~':
        return (evaluate(expr.first, context)).__invert__();
    case '+':
        if (!expr.second) {
            return py.PY_positive(evaluate(expr.first, context));
        }
    case '-':
        if (!expr.second) {
            return py.PY_negative(evaluate(expr.first, context));
        }
    case '*': case '/': case '//':
    case '%':
    case '**':
    case '<<': case '>>':
    case '&': case '^': case '|':
        return PY_op(
            evaluate(expr.first, context),
            evaluate(expr.second, context),
            expr.id);

    default:
        throw new Error('SyntaxError: Unknown node [[' + expr.id + ']]');
    }
};

function PY_ensurepy(val, name) {
        switch (val) {
        case undefined:
            throw new Error("NameError: name '" + name + "' is not defined");
        case null:
            return py.None;
        case true:
            return py.True;
        case false:
            return py.False;
        }

        var fn = function () {};
        fn.prototype = py.object;
        if (py.PY_isInstance(val, py.object)
            || py.PY_isSubclass(val, py.object)) {
            return val;
        }

        switch (typeof val) {
        case 'number':
            return py.float.fromJSON(val);
        case 'string':
            return py.str.fromJSON(val);
        case 'function':
            return py.PY_def.fromJSON(val);
        }

        switch(val.constructor) {
        case Object:
            // TODO: why py.object instead of py.dict?
            var o = py.PY_call(py.object);
            for (var prop in val) {
                if (val.hasOwnProperty(prop)) {
                    o[prop] = val[prop];
                }
            }
            return o;
        case Array:
            return py.list.fromJSON(val);
        }

        throw new Error("Could not convert " + val + " to a pyval");
    }

var PY_decode_string_literal = function (str, unicode) {
    var out = [], code;
    // Directly maps a single escape code to an output
    // character
    var direct_map = {
        '\\': '\\',
        '"': '"',
        "'": "'",
        'a': '\x07',
        'b': '\x08',
        'f': '\x0c',
        'n': '\n',
        'r': '\r',
        't': '\t',
        'v': '\v'
    };

    for (var i=0; i<str.length; ++i) {
        if (str[i] !== '\\') {
            out.push(str[i]);
            continue;
        }
        var escape = str[i+1];
        if (escape in direct_map) {
            out.push(direct_map[escape]);
            ++i;
            continue;
        }

        switch (escape) {
        // Ignored
        case '\n': ++i; continue;
        // Character named name in the Unicode database (Unicode only)
        case 'N':
            if (!unicode) { break; }
            throw Error("SyntaxError: \\N{} escape not implemented");
        case 'u':
            if (!unicode) { break; }
            var uni = str.slice(i+2, i+6);
            if (!/[0-9a-f]{4}/i.test(uni)) {
                throw new Error([
                    "SyntaxError: (unicode error) 'unicodeescape' codec",
                    " can't decode bytes in position ",
                    i, "-", i+4,
                    ": truncated \\uXXXX escape"
                ].join(''));
            }
            code = parseInt(uni, 16);
            out.push(String.fromCharCode(code));
            // escape + 4 hex digits
            i += 5;
            continue;
        case 'U':
            if (!unicode) { break; }
            // TODO: String.fromCodePoint
            throw Error("SyntaxError: \\U escape not implemented");
        case 'x':
            // get 2 hex digits
            var hex = str.slice(i+2, i+4);
            if (!/[0-9a-f]{2}/i.test(hex)) {
                if (!unicode) {
                    throw new Error('ValueError: invalid \\x escape');
                }
                throw new Error([
                    "SyntaxError: (unicode error) 'unicodeescape'",
                    " codec can't decode bytes in position ",
                    i, '-', i+2,
                    ": truncated \\xXX escape"
                ].join(''))
            }
            code = parseInt(hex, 16);
            out.push(String.fromCharCode(code));
            // skip escape + 2 hex digits
            i += 3;
            continue;
        default:
            // Check if octal
            if (!/[0-8]/.test(escape)) { break; }
            var r = /[0-8]{1,3}/g;
            r.lastIndex = i+1;
            var m = r.exec(str);
            var oct = m[0];
            code = parseInt(oct, 8);
            out.push(String.fromCharCode(code));
            // skip matchlength
            i += oct.length;
            continue;
        }
        out.push('\\');
    }

    return out.join('');
};



return {
    sync_eval_domains_and_contexts: sync_eval_domains_and_contexts,
};

});