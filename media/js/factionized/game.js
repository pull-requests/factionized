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
		thread.log = $('<div />').addClass('fz-log');
		thread.model = new FZ.Thread(thread.raw,
									thread.log);
		parent.append(
			thread.form = $('<form />').append(
				thread.log,
				thread.input = $('<textarea />').
					attr({ rows: 10, cols: 2 }).
					addClass('fz-message'),
				thread.button = $('<a />').
					attr('href', 'javascript:void(0)').
					addClass('fz-button').
					append('Send').
					click(function() {
						thread.model.send(thread.input.val());
						thread.input.val('');
						return false;
					})
				)
			);
		thread.model.onmessage.bind(function(message) {
			$('<div />').
				addClass('fz-message').
				append(message).
				appendTo(thread.log);
		});
		thread.input.wrap('<div class="fz-textarea fz-wrapper"></div>');
	};

	// Clears out parent html and removes pre-existing data
	var destroy = function() {
		parent.removeData('game')
		parent.html('');
		api = undefined;
		config = undefined;
	}

})( jQuery, FZ );
