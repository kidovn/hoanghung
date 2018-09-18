$(document).ready(function() {
    $(".save").click(function(){

        var task = {};
        var new_id = 0;
        var table = document.getElementsByTagName('table')[0];
        var rows = table.rows;
        for (var i = 2; i < rows.length; i++) {
            var rowText = rows[i].firstChild.textContent;
            if (rows[i].cells.length>5){
                for (var j=0; j< (rows[i].cells.length-5)/3;j++){
                    console.log(5+j*3);
                    var target = rows[i].cells[5+j*3].children[0].value;
                    var achieve = rows[i].cells[5+j*3+1].children[0].value;
                    if (rows[i].cells[5+j*3].children[0].hasAttribute('data-id')){
                        var id = rows[i].cells[5+j*3].children[0].getAttribute('data-id');
                        task[id] = {
                            'target':target,'achieve':achieve
                        };
                    }
                    else{
                        var job_id = rows[i].cells[5+j*3].children[0].getAttribute('job-id');
                        var employee_id = rows[i].cells[5+j*3].children[0].getAttribute('employee-id');
                        new_id+=1;
                        task['var'+new_id] = {
                            'target':target,'achieve':achieve,'job_id':job_id,'employee_id':employee_id
                        };
                    }

                }
            }
        }

        $.ajax({
          type: 'post',
          url: '/push_task',
          data: {'data':JSON.stringify(task)},
//          data_type: 'json',
          success: function(result) {
            // check result object for what you returned
//            alert('done');
          },
          error: function(error) {
            // check error object or return error
            console.log(error)
//            alert(error.message);
          }
        });

    });
});