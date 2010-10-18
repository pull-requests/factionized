(function( $, FZ ) {

	var parent,
		config;

	var init = function() {
		parent.append('Hello');
	}

	$.fn.game = function(config) {
		parent = $(this).first();
		config = config;
		init();
	}

})( jQuery, FZ );
