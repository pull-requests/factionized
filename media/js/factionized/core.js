(function( $ ) {

	this.FZ = this.FZ || {};
	
	this.FZ.from_timestamp = function(stamp) {
		var dat = new Date(stamp * 1000);
		var mins = dat.getMinutes();
		if( mins < 10 ) { mins = '0' + mins; }
		return (dat.getMonth() + '-' + dat.getDate() + '-' + dat.getFullYear() + ' @ ' + dat.getHours() + ':' + mins);
	};

})( jQuery );
