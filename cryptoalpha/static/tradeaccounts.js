$( "#tickerauto" ).autocomplete({
  source: function( request, response ) {
     console.log("Here")
    $.ajax( {
      url: "/xglst",
      dataType: "json",
      data: {
        term: request.term
      },
      success: function( data ) {
          console.log(data)
          response($.map(data, function(item) {
              return {
                label: item,
                value: item
              }
          }));
      }
    } );
  },
  minLength: 2
} );
