(function( $, BB, FZ ) {

	var Thread = FZ.Thread = BB.Model.extend({
		initialize: function(thread) {
			this.id = thread.uid
			this.raw = thread;
			this.round = thread.round;
			this.game = thread.round.game;
			var loc = window.location;
			this.stream = FZ.poll('/' + this.stream_url());
			this.stream.bind($.proxy(function(data) {
				this.onmessage.trigger.call(this, data);
			}, this));
		},
		thread_url: function() {
			return [
				'games', this.game.uid,
				'rounds', this.round.uid,
				'threads', this.id
			].join('/');
		},
		stream_url: function() {
			return this.thread_url() + '/activities';
		},
		listen: function() {
			console.log(this.last)
			this.stream.
				from(this.last.uid).
				start();
		},
		unlisten: function() {
			this.stream.stop();
		},
		send: function(content, callback) {
			$.post('/' + this.thread_url() + '/messages', { content: content }, $.proxy(function(data) {
				if( $.isFunction(callback) ) {
					callback(this, data);
				}
			}, this));
		},
		activities: function(callback) {
			$.get('/' + this.thread_url() + '/activities', $.proxy(function(data) {
				this.update_last(data);
				if( $.isFunction(callback) ) {
					callback(data);
				}
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
				this.update_last(msg);
				evt.trigger('received', msg);
			}
			return api;
		})(),
		update_last: function(data) {
			data = $.makeArray(data);
			var dat = data[data.length-1];
			if( dat ) {
				this.last = dat;
			}
			return this;
		}
	});

})( jQuery, Backbone, FZ );
