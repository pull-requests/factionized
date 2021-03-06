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

                // Voting summary
                var vote_summary = $('<div></div>').
                    attr('class', 'fz-votesummary').
                    attr('id', 'votesummary_' + t.uid).
                    appendTo(thread_vote);

                var vote_select = $('<select></select>').
                    attr('id', "vote_select_" + t.uid).
                    attr('name', "vote_select_" + t.uid);

                init_data.player_list.forEach(function(p) {
                    $('<option></option>').attr('value', p.uid).
                    append(p.name).appendTo(vote_select);
                });

                var vote_action = function() {
                    var vote_uid = vote_select.find(":selected").val();
                    var path = '/games/' + game.uid;
                    path = path + '/rounds/' + init_data.rounds.uid;
                    path = path + '/threads/' + t.uid;
                    path = path + '/votes';
                    var data = {'target_id': vote_uid};
                    $.post(path, data, function() {
                        console.log('Voted for '+ vote_uid);
                        update_summary(game.uid,
                                       init_data.rounds.uid,
                                       t.uid);
                    });
                }

                vote_select.appendTo(thread_vote);
                $('<span class="fz-button">Vote</span>').
                    attr('href', 'javascript:void(0)').
                    click(vote_action).
                    appendTo(thread_vote);
                thread_vote.appendTo(parent);
                
                //update summary
                update_summary(game.uid, init_data.rounds.uid, t.uid);
            });
        }
	}

	var start_game = function(game) {
		$.post('/games/' + game.uid + '/start', function() {
			console.log('Game started');
		});
	}

    var update_summary = function(game_uid, round_uid, thread_uid) {
        var old_summary = $('#votesummary_' + thread_uid);
        var vote_summary = $('<div></div>').
            attr('class', 'fz-votesummary').
            attr('id', 'votesummary_' + thread_uid);

        var summary_path = '/games/' + game_uid;
        summary_path += '/rounds/' + round_uid;
        summary_path += '/threads/' + thread_uid;
        summary_path += '/vote_summary';
        $.get(summary_path, function(data) {
            if (data.summaries.length > 0) {
                var sum_list = $('<ul></ul>');
                data.summaries.forEach(function(s) {
                    $('<li></li>').
                        append(s.profile.name + ': ' + s.total).
                        appendTo(sum_list);
                });
                sum_list.appendTo(vote_summary);
                $('<img/>').
                    attr('src', data.chart_url).
                    appendTo(vote_summary);
            }
        });
        old_summary.replaceWith(vote_summary);
    }

	var join_game = function(game) {
		var path = '/games/' + game.uid + '/join';
		$.post(path, function(data, statusText) {
			if(statusText == 'success') {
				window.location = window.location;
			}
		});
	}

})( jQuery );
