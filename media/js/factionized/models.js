(function( $, BB, FZ ) {

	var Thread = FZ.Thread = BB.Model.extend({
		initialize: function(thread) {
			this.id = thread.uid
			this.raw = thread;
			this.round = thread.round;
			this.game = thread.round.game;
			this.socket = new io.Socket(this.stream_url());
			this.socket.on('message', this.onmessage.trigger);
		},
		thread_url: function() {
			return [
				'/games', this.game.uid,
				'rounds', this.round.uid,
				'threads', this.id
			].join('/');
		},
		stream_url: function() {
			return this.thread_url() + '/activities/stream';
		},
		send: function(content, callback) {
			$.post(this.thread_url() + '/messages', { content: content }, $.proxy(function() {
				if( $.isFunction(callback) ) {
					callback(this, content);
				}
				this.onmessage.trigger(content);
			}, this));
		},
		onmessage: (function() {
			var evt = {};
			_.extend(evt, Backbone.Events);
			var api = {};
			api.bind = function(cb) {
				evt.bind('received', cb);
			}
			api.unbind = function(cb) {
				evt.unbind('received', cb);
			}
			api.trigger = function(msg) {
				evt.trigger('received', msg);
			}
			return api;
		})()
	});

})( jQuery, Backbone, FZ );