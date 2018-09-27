var http = require('http');
var formidable = require('formidable');
var fs = require('fs');
var shell = require('shelljs');
var filepath = '/opt/recall_registry/fileupload/';
var scriptpath = '/opt/recall_registry/';

http.createServer(function (req, res) {
  if (req.url == '/fileupload') {
    var form = new formidable.IncomingForm();
    form.parse(req, function (err, fields, files) {
      var orgfilename = files.filetoupload.name;
      var filename = orgfilename.split(' ').join('_');	    
      var oldpath = files.filetoupload.path;
      var newpath = filepath + filename;
      fs.rename(oldpath, newpath, function (err) {
        if (err) throw err;
        // Run external tool synchronously
	if (shell.exec('python ' + scriptpath + 'recall.py '+ filename).code !== 0) {
            shell.echo('Error: Recall script eror');
            shell.exit(1);
        }else{
            fs.readFile(filepath + 'final_' + filename.replace('xls','csv'), function (err, content) {
            if (err) {
                 res.writeHead(400, {'Content-type':'text/html'})
                 console.log(err);
                 res.end("No such file");
           } else {
                 //specify Content will be an attachment
                 res.setHeader('Content-disposition', 'attachment; filename=Cleansed_'+orgfilename.replace('xls','csv'));
                 res.end(content);
            	 filename = filename.replace('xls','csv')
		 console.log('attempting to remove ',filepath + filename)
		 console.log('attempting to remove ',filepath + 'output_' + filename)
		 console.log('attempting to remove ',filepath + 'final_' + filename)
		 shell.rm('-rf', filepath + filename);
         	 shell.rm('-rf', filepath + orgfilename.split(' ').join('_'));
                 shell.rm('-rf', filepath + 'output_' + filename);
                 shell.rm('-rf', filepath + 'final_' + filename);
                 console.log('removing uploaded files', filename)
             }
           });
       }
     });
 });
  } else {
	    fs.readFile(scriptpath + 'form.html', function(err, data) {
	            if (err) {
        	        res.writeHead(400, {'Content-type':'text/html'})
                	console.log(err);
                	res.end("No such file");
	           } else {
		    	res.writeHead(200, {'Content-Type': 'text/html'});
		    	res.write(data);
		    	res.end();
		   }
	     });
/*
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write('<h1>Recall Registry Cleanser</h1>');  
    res.write('<label> Upload .xls file from recal registry</label>');
    res.write('<form action="fileupload" method="post" enctype="multipart/form-data">');
    res.write('<input type="file" name="filetoupload"><br><br>');
    res.write('<input type="submit" value="Process & Download">');
    res.write('</form>');
    return res.end();
*/
  }
}).listen(3000); 
