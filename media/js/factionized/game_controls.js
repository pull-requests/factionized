(function( $ ) {

	$.fn.game_controls = function(game, profile) {
		$(this).each(function() {
			install($(this), game, profile);
		});
	};

	var install = function(parent, game, profile) {
		parent.addClass('fz-game fz-controls');
		if(game.started) {
			$('<span class="fz-started">Game has already started</span>').appendTo(parent);
		} else {
			$('<a class="fz-start" href="javascript:void(0)">Start Game</a>').
				click(function() { start_game(game) }).
				appendTo(parent);
		}
		if( _.indexOf(game.signups, profile.uid) >= 0 ) {
			$('<span />').
				append(
					game.game_starter.uid == profile.uid ?
						'You Started this Game!' :
						'You have Joined this Game!'
				).
				appendTo(parent);
		} else {
			$('<a />').
				addClass('fz-join').
				attr('href', 'javascript:void(0)').
				append('Join Game').
				click(function() { join_game(game, profile); }).
				appendTo(parent);
		}
	}

	var start_game = function(game) {
		$.post('/games/' + game.uid + '/start', function() {
			console.log('Game started');
		});
	}

	var join_game = function(game) {
		var path = '/games/' + game.uid + '/join';
		console.log(path);
		$.post(game, function() {
			console.log('User Joined game');
		});
	}

})( jQuery );
