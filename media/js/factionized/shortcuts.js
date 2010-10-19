(function( $ ) {

	// Plugin entrypoint
	$.fn.shortcuts = function(cmd) {
		cmd = cmd || {};
		$(this).filter('textarea').each(function() {
			if( $(this).data('shortcuts') ) {
				$(this).data('shortcuts').destroy();
				$(this).removeData('shortcuts');
			}
			if( cmd != 'destroy') {
				$(this).data('shortcuts', new Shortcuts($(this), cmd));
			}
		});
		return $(this);
	};

	var Shortcuts = function(node, config) {
		this.node = node;
		this.node.keydown($.proxy(this.down, this));
		this.node.keyup($.proxy(this.up, this));
		if( config.submit ) {
			this.callbacks.submit = config.submit;
		}
		this.register('down', '13', $.proxy(this.submit, this));
		this.register('down', '9', $.proxy(this.tab, this));
	};

	Shortcuts.prototype = {
		callbacks: {},
		queue: [],
		commands: { down: {}, up: {} },
		register: function(command, sig, callback) {
			if( this.commands[command] ) {
				this.commands[command][sig] = callback;
			}
		},
		down: function(e) {
			this.queue.push(e.keyCode);
			var command = this.commands.down[_.reduce(this.queue,
				function(result, code) {
					return result ? (result + '+' + code) : code;
				}
			)];
			if( $.isFunction(command) ) {
				if( command.call(e, this.node) ) {
					e.preventDefault();
				}
			}
		},
		up: function(e) {
			var command = this.commands.up[_.reduce(this.queue,
				function(result, code) {
					return result ? (result + '+' + code) : code;
				}
			)];
			if( $.isFunction(command) ) {
				if( command.call(e, this.node) ) {
					e.preventImmediatePropagation();
				}
			}
			this.queue = _.without([e.keycode]);
		},
		submit: function() {
			var val = this.node.val();
			if( $.isFunction(this.callbacks.submit) ) {
				this.node.val('');
				this.callbacks.submit.call(this.node, val);
				return true;
			}
		},
		tab: function() {
			this.node.val(this.node.val() + '\t');
			return true;
		}
	};

})( jQuery );
