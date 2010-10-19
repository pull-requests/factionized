(function( $, _, BB, FZ ) {

	FZ.poll = function(config) {
		if( typeof(config) == 'string' ) {
			config = { path: config };
		}
		return new poller(config);
	};

	var _event = function() {
		_.extend(this, BB.Events);
	}

	var poller = function(config) {
		this.config = config || {};
		var evt = new _event();
		this.bind = function(cb) {
			evt.bind('received', cb);
		};
		this.unbind = function(cb) {
			evt.unbind('received', cb);
		};
		this.trigger = function(data) {
			evt.trigger('received', data);
		};
		this.stopped = true;
		this.from();
	}

	poller.prototype = {
		start: function() {
			if( this.stopped ) {
				this.stopped = false;
				this.tick();
			}
		},
		stop: function() {
			this.stopped = true;
		},
		from: function(dat) {
			this.since = (dat || new Date());
			return this;
		},
		tick: function() {
			if( this.stopped ) { return; }
			this.get();
			setTimeout($.proxy(this.tick, this), this.config.interval || 1000);
		},
		get: function() {
			if( this.locked ) { return; }
			this.locked = true;
			$.get(this.config.path + '/xhr-polling/' + this.since.valueOf(), $.proxy(function(data) {
				data = $.makeArray(data);
				var dat = data[data.length-1];
				if( dat && dat.created ) {
					this.since = new Date(dat.created * 1000);
				}
				this.locked = false;
				this.trigger(data);
			}, this));
		}
	};

})( jQuery, _, Backbone, FZ );
