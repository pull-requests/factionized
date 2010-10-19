(function( $, FZ ) {

	var parent,
		config,
		api = {};

	// Plugin entry point. Assumes there is only one game viewport
	// so it destroys any pre-existing games and then proceeds
	// with installation
	var init = $.fn.game = function(conf) {
		if( parent ) {
			parent.data('game').destroy();
		}
		parent = $(this).first();
		config = conf;
		install();
	}

	// Sets up the game api object and kicks off the installation process
	var install = function() {
		api = parent.data('game', {});
		api.destroy = destroy;
		install.tabs(install.thread);
	}

	// Adds the tabbing containers for threads and instantiates the tabs.
	install.tabs = function(content_callback) {
		api.tabs.root = $('<div />').
			hide().
			addClass('fz-tabs').
			append(
				api.tabs.labels = $('<div class="fz-labels"></div>'),
				api.tabs.panes = $('<div class="fz-panes"></div>')
			).
			appendTo(parent);
		$.each(config.threads, function(k, thread) {
			$('<a href="javascript:void(0)" class="fz-label"></a>').
				addClass('fz-thread fz-label fz-id-' + thread.uid).
				append(thread.name).
				appendTo(api.tabs.labels);
			var pane = $('<div />').
				addClass('fz-thread fz-pane fz-id-' + thread.uid).
				appendTo(api.tabs.panes);
			(content_callback || $.noop)(pane, thread);
		});
		api.tabs.labels.tabs('> .fz-panes', {
			tabs: 'fz-pane',
			current: 'fz-current'
		});
		api.tabs.api = api.tabs.labels.data('tabs');
		api.tabs.pane = function(id) {
			return api.tabs.panes.find('> fz-id-' + id).first();
		};
		api.tabs.root.show();
	};

	install.thread = function(parent, thread) {
		api.threads = api.threads || {};
		thread = api.threads[thread.uid] = { raw: thread };
		thread.log = $('<table />').addClass('fz-log');
		thread.model = new FZ.Thread(thread.raw,
									thread.log);
		var submit = function(content) {
			thread.model.send($.trim(content))
			thread.input.val('');
		};
		var print = function(messages) {
			var follow = at_bottom();
			$.each($.makeArray(messages), function(k,v) {
				var tab = '&nbsp;&nbsp;';
				tab = tab + tab + tab + tab;
				var content = parse(v);
				content.content = content.content.replace(/\n/g, '<br />').replace(/\t/g, tab);
				$('<tr />').
					addClass('fz-message fz-' + v['class'].toLowerCase().replace(/ /g, '-')).
					append(
						$('<td class="fz-meta" />').append(
							$('<span />').addClass('fz-label').append(content.label),
							$('<span />').
								addClass('fz-created').
								append(FZ.from_timestamp(v.created))
						),
						$('<td class="fz-content" />').append(content.content)
					).
					appendTo(thread.log);
				if(follow) { goto_bottom(); }
			});
			if( !follow ) {
				var count = parseInt(thread.notices.find('fz-count').text(), 10);
				thread.notices.slideDown(function() {
					thread.notices.find('fz-count').text((count || 0) + 1);
				});
			}
		};
		
		var goto_bottom = function() {
			thread.log[0].scrollTop = thread.log[0].scrollHeight;
		};
		var at_bottom = function() {
			var node = thread.log[0];
			return (node.scrollHeight - node.scrollTop - $(node).height()) < 50;
		}
		parent.append(
			thread.form = $('<form />').append(
				thread.log,
				thread.notices = $('<div />').
					addClass('.fz-notices').hide().
					append(
						'<span class="fz-count"></span>',
						'<span class="fz-message">Unread Messages</span>'
					),
				thread.input = $('<textarea />').
					attr({ rows: 10, cols: 2 }).
					addClass('fz-message').
					shortcuts({ submit: submit }),
				thread.button = $('<a />').
					attr('href', 'javascript:void(0)').
					addClass('fz-button').
					append('Send').
					click(function() {
						submit(thread.input.val())
						e.preventDefault();
					})
				)
			);
		thread.log.scroll(function() {
			if( at_bottom() ) {
				thread.notices.slideUp('fast', function() {
					thread.notices.find('.fz-count').text('');
				});
			}
		});
		thread.model.activities(function(msgs) {
			print(msgs);
			thread.model.onmessage.bind(print);
			thread.model.listen()
		});
		thread.input.wrap('<div class="fz-textarea fz-wrapper"></div>');
	};

	var parse = function(msg) {
		return parse[msg['class'].toLowerCase().replace(/ /g, '-')](msg);
	};

	parse.playerjoin = function(msg) {
		var id = msg.actor.player.name || msg.actor.player.user.email;
		return {
			label: 'Game Notice',
			content: 'Player ' + id + ' joined the game.'
		};
	};

	parse.save = function(msg) {
		return {
			label: (msg.actor.player.name || msg.actor.player.user.email),
			content: (msg.target.player.name || 
						msg.targe.player.user.email) + 
						' was saved by the doctor!'
		}
	};
	parse.reveal = function(msg) {
		return {
			label: (msg.actor.player.name || msg.actor.player.user.email),
			content: (msg.target.player.name || msg.target.player.user.email) + 
				' was revealed to be a ' + msg.target.name
		}
	};

	parse.message = function(msg) {
		return {
			label: (msg.actor.player.name || msg.actor.player.user.email),
			content: msg.content
		}
	};

	parse.deathbyvote = function(msg) {
		return {
			label: 'Game Notice',
			content: (msg.actor.player.name || msg.actor.player.user.email) +
				' was killed by ' + 
				(msg.vote_thread.name === 'Vanillager' ? 'vote' : 'mafia')
		}
	};

	parse.vote = function(msg) {
		return {
			label: (msg.actor.player.name || msg.actor.player.user.email),
			content: '!vote for ' + 
				(msg.target.player.name || msg.actor.player.user.email)
		}
	}

	// Clears out parent html and removes pre-existing data
	var destroy = function() {
		parent.removeData('game')
		parent.html('');
		api = undefined;
		config = undefined;
	}

})( jQuery, FZ );
