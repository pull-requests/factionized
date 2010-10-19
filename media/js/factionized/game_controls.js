(function( $ ) {

	$.fn.game_controls = function(game, profile) {
		$(this).each(function() {
			install($(this), game, profile);
		});
	};

	var install = function(parent, init_data) {
        var game = init_data.game;
        var profile = init_data.profile;
		parent.addClass('fz-game fz-controls');
		if(game.started) {
			$('<span class="fz-started fz-button fz-inactive">Game has already started</span>').appendTo(parent);
		} else {
			$('<a class="fz-start fz-button" href="javascript:void(0)">Start Game</a>').
				click(function() { start_game(game) }).
				appendTo(parent);
		}
		if( _.indexOf(game.signups, profile.uid) >= 0 ) {
			$('<span class="fz-button fz-inactive" />').
				append(
					game.game_starter.uid == profile.uid ?
						'You Started this Game!' :
						'You have Joined this Game!'
				).
				appendTo(parent);
		} else {
			$('<a />').
				addClass('fz-join fz-button').
				attr('href', 'javascript:void(0)').
				append('Join Game').
				click(function() { join_game(game, profile); }).
				appendTo(parent);
		}

        // voting controls
        if (game.started) {
            init_data.threads.forEach(function(t) {
                var thread_vote = $('<div></div>').
                    attr('class', 'fz-votewrap').
                    attr('id', 'votewrap_' + t.uid);
                $('<h3>' + t.name + ' Vote</h3>').
                    appendTo(thread_vote);

                var vote_select = $('<select></select>').
                    attr('id', "vote_select_" + t.uid).
                    attr('name', "vote_select_" + t.uid);

                init_data.player_list.forEach(function(p) {
                    $('<option></option>').attr('value', p.uid).
                    append(p.name).appendTo(vote_select);
                });

                vote_select.appendTo(thread_vote);
                $('<span class="fz-button">Vote</span>').
                    attr('href', 'javascript:void(0)').
                    appendTo(thread_vote);
                thread_vote.appendTo(parent);
            });
        }
	}

	var start_game = function(game) {
		$.post('/games/' + game.uid + '/start', function() {
			console.log('Game started');
		});
	}

	var join_game = function(game) {
		var path = '/games/' + game.uid + '/join';
		$.post(path, function() {
			console.log('User Joined game');
		});
	}

})( jQuery );
