   require([
            "jquery",
            "splunkjs/mvc/searchmanager",
            "splunkjs/mvc/simplexml/ready!"
          ], function(
              $,
              SearchManager
          ) {
              var mysearch = new SearchManager({
                  id: "mysearch",
                  autostart: "false",
                  search: "`create_lookup`" 
              });
              $(".button1").on("click", function (){
                  var ok = confirm("create lookup?");
                  if (ok){
                      mysearch.startSearch();
                      alert('lookup created');
		      setTimeout("location.reload();", 0);
                  } //else {
                  //    alert('user did not click ok!');
                  //}
              });
         });
