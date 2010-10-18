(function( $ ) {

	$.fn.game_controls = function(game) {
		$(this).each(function() {
			install($(this), game);
		});
	};

	var install = function(parent, game) {
		if(game.started) {
			$('<span>Game has already started</span>').appendTo(parent);
		} else {
			$('<a href="javascript:void(0)">Start Game</a>').
				click(function() { start_game(game) }).
				appendTo(parent);
		}
	}

	var start_game = function(game) {
		$.post('/games/' + game.uid + '/start', function() {
			console.log('Game started');
		});
	}

})( jQuery );
