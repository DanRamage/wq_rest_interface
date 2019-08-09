//Various helper functions
Math.roundTo = function(val, dec) {
  if (!isNaN(val)) {
    var mult = Math.pow(10,dec);
    return ( Math.round(val*mult) / mult );
  }
  else {
    return val;
  }
};

//Define key global variables and arrays
var userLat;
var userLng;
var dateSet;
var onlineStatus = 'on';

var current_date = new Date();
var markerType = 'forecast'; //Initial markers set to show forecast results

var advisory_limits;
//var predictionData = {};
//var currentEtcoc = {};
var wq_site_name = "";
var wq_site_bbox;
var site;
var stations_records;

/*
This object is to consolidate the prediction and sample data into one place and provide
a common interface. Want to move away from using the 2 json objects in the code and simply
use them to construct one object.
 */
function stationData()
{
  var self = this;
  self.station = undefined;
  self.site_type = undefined;
  self.latitude = undefined;
  self.longitude = undefined;
  self.description = undefined;
  self.region = undefined;
  //Prediction related vars
  self.forecast_date = undefined;
  self.station_message = undefined;
  self.message_severity = undefined;
  self.ensemble_result = undefined;
  //Sample related vars
  self.sample_date = undefined;
  self.sample_value = undefined;
  self.issues_advisories = undefined;
  self.advisory_message = undefined;
  /*
  self.set_prediction_data = function(station_name, prediction_data)
  {

  };
  self.set_advisory_data = function(station_name, advisory_data)
  {

  };
  */
  self.Station = function()
  {
    return self.station;
  };
  self.SiteType = function()
  {
    return self.site_type;
  };
  self.Location = function()
  {
    return([self.longitude, self.latitude]);
  };
  self.Description = function()
  {
    return(self.description);
  };
  self.Region = function()
  {
    return(self.region);
  };
  self.ForecastDate = function()
  {
    return(self.forecast_date);
  };
  self.EnsembleResult = function()
  {
    return(self.ensemble_result);
  };
  self.ForecastStationMessage = function()
  {
    return(self.station_message);
  };
  self.ForecastStationMessageSeverity = function()
  {
    return(self.message_severity);
  };
  self.SampleDate = function()
  {
    return (self.sample_date);
  };
  self.SampleValue = function()
  {
    return(self.sample_value);
  };
  self.IssuesAdvisories = function()
  {
    return(self.issues_adivisories);
  };
  self.SampleStationMessage = function()
  {
    return(self.advisory_message);
  };

};

function stationsData()
{
  var self = this;

  self.station_data_records = {};

  self.build_records = function(data_records)
  {
    var advistory_data = data_records['advisory_data'];
    var prediction_data = data_records['prediction_data'];
    var other_sites = data_records['sites']

    $.each(advistory_data.features, function(data_ndx, feature)
    {
      var data_rec = new stationData();
      var station = String(feature.properties.station);
      data_rec.station = station;
      data_rec.latitude = feature.geometry.coordinates[1];
      data_rec.longitude = feature.geometry.coordinates[0];
      data_rec.description = feature.properties.desc;
      data_rec.sample_date = feature.properties.test.beachadvisories.date;
      if(typeof(feature.properties.test.beachadvisories.value) == 'array') {
        data_rec.sample_value = feature.properties.test.beachadvisories.value[0];
      }
      else {
        data_rec.sample_value = feature.properties.test.beachadvisories.value;
      }
      data_rec.issues_adivisories = feature.properties.issues_advisories;
      data_rec.advisory_message = 'None';
      if(feature.properties.advisory !== undefined && feature.properties.advisory.length)
      {
        data_rec.advisory_message = feature.properties.advisory;
      }
      self.station_data_records[station] = data_rec;
    });

    $.each(prediction_data.contents.stationData.features, function(data_ndx, feature)
    {
      var station = feature.properties.station;
      var data_rec = self.station_data_records[station];
      if(data_rec !== undefined)
      {
        if(data_rec.forecast_date === undefined)
        {
          data_rec.forecast_date = prediction_data.contents.run_date;
        }
        data_rec.station_message = "";
        data_rec.message_severity = "";
        if(feature.properties.site_message !== undefined) {
          data_rec.station_message = feature.properties.site_message.message;
          data_rec.message_severity = feature.properties.site_message.severity;
        }
        data_rec.ensemble_result = 'None';
        if(feature.properties.ensemble !== undefined && feature.properties.ensemble.length)
        {
          data_rec.ensemble_result = feature.properties.ensemble;
        }
      }
      //We've got a station that has predictions but no sampling data.
      else
      {
        var data_rec = new stationData();
        data_rec.station = feature.properties.station;
        data_rec.latitude = feature.geometry.coordinates[1];
        data_rec.longitude = feature.geometry.coordinates[0];
        data_rec.description = feature.properties.desc;
        self.station_data_records[data_rec.station] = data_rec;
        if(data_rec.forecast_date === undefined)
        {
          data_rec.forecast_date = prediction_data.contents.run_date;
        }
        data_rec.station_message = "";
        data_rec.message_severity = "";
        if(feature.properties.site_message !== undefined) {
          data_rec.station_message = feature.properties.site_message.message;
          data_rec.message_severity = feature.properties.site_message.severity;
        }
        data_rec.ensemble_result = 'None';
        if(feature.properties.ensemble !== undefined && feature.properties.ensemble.length)
        {
          data_rec.ensemble_result = feature.properties.ensemble;
        }
      }
    });

    $.each(other_sites.features, function(data_ndx, feature)
    {
      var data_rec = new stationData();
      var station = String(feature.properties.station);
      data_rec.station = station;
      data_rec.site_type = feature.properties.site_type;
      data_rec.latitude = feature.geometry.coordinates[1];
      data_rec.longitude = feature.geometry.coordinates[0];
      data_rec.description = feature.properties.desc;
      self.station_data_records[station] = data_rec;
    });

  };
  self.StationData = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec);
  };
  self.SiteType = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.SiteType());
  }
  self.Location = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.Location());
  };
  self.Description = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.Description());
  };
  self.Region = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.Region());
  };
  self.SampleValue = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.SampleValue())
  };
  self.SampleDate = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.SampleDate());
  };
  self.IssuesAdvisories = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.IssuesAdvisories());

  }
  self.EnsembleResult = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.EnsembleResult());
  };
  self.ForecastDate = function(station_name)
  {
    var data_rec = self.station_data_records[station_name];
    return(data_rec.ForecastDate());
  };
}

function initialize_app(site_name, data, limits) {
  site = site_name;
  advisory_limits = limits;
  stations_records = new stationsData();
  stations_records.build_records(data);
  /*
  if(data['prediction_data'].contents !== null ) {
    var forecast_date = data['prediction_data'].contents.testDate;
    $.each(data['prediction_data'].contents.stationData.features, function (i, beach) {
      predictionData[beach.properties.station] = {
        "station": beach.properties.station,
        "desc": beach.properties.desc,
        "ensemble": beach.properties.ensemble,
        "forecast_date": forecast_date,
        "message": beach.properties.message,
        "region": beach.properties.region,
        "lat": beach.geometry.coordinates[1],
        "lng": beach.geometry.coordinates[0]
      };
    });
  }
  */
  /*
  $.each(data['advisory_data'].features, function(s,stations){
    permanentAdvisory = stations.properties.sign;

    $.each(stations.properties.test, function(i,j){

      //Determine if an advisory is in place (permanent or temporary based on ETCOC of 104)
      if(('advisory' in stations.properties) == false)
      {
        if (parseInt(j.value, 10) >= limits['High'].min_limit || permanentAdvisory === true) {
          if (permanentAdvisory === true) {
            advisoryText = 'Long Term';
          }
          else {
            advisoryText = 'Yes';
          }
        }
        else {
          advisoryText = 'None';
        }
      }
      else {
        advisoryText = stations.properties.advisory;
      }

      currentEtcoc[stations.properties.station] = {
        "desc" : stations.properties.desc,
        "date" : j.date,
        "lat" : stations.geometry.coordinates[1],
        "lng" : stations.geometry.coordinates[0],
        "value" : j.value,
        "advisory" : advisoryText,
        "issues_advisories": stations.properties.issues_advisories
      };

    });

  });
  */

  $("#about_page").on("click", function() {
      var i = 0;
  });


  return;
}


function days_between(date1, date2) {

    // The number of milliseconds in one day
    var ONE_DAY = 1000 * 60 * 60 * 24;

    // Convert both dates to milliseconds
    var date1_ms = date1.getTime();
    var date2_ms = date2.getTime();

    // Calculate the difference in milliseconds
    var difference_ms = Math.abs(date1_ms - date2_ms);

    // Convert back to days and return
    return Math.round(difference_ms/ONE_DAY);

}


function toRad(degrees){
    return degrees * Math.PI / 180;
}

function calcDistance(lat1,lng1,lat2,lng2){
  var R = 6371; // Radius of the earth in km
  var dLat = toRad(lat2-lat1);  // Javascript functions in radians
  var dLng = toRad(lng2-lng1);
  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
          Math.sin(dLng/2) * Math.sin(dLng/2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  var d = R * c; // Distance in km
  return d;
}


function GetURLParameter(sParam)
{
  var sPageURL = window.location.search.substring(1);
  var sURLVariables = sPageURL.split('&');
  for (var i = 0; i < sURLVariables.length; i++)
  {
    var sParameterName = sURLVariables[i].split('=');
    if (sParameterName[0] == sParam)
    {
      return sParameterName[1];
    }
  }
  return null;
}

function GetSiteFromURL(url)
{
  //Split the domain components up to get the subdomain which should be the
  //site of interest.
  //var domain_components= url.split('.');
  var path = url.split('/');
  return(path[1]);
}
function strtr(str,list){
  for( var c in list ){
    str = String(str).replace( new RegExp( c ,"g"), list[c] );
  }
  return str;
}

function capitalize (text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}


function getScreenSize(dimension){
  if(dimension == 'width'){
    return window.innerWidth ? window.innerWidth : $(window).width();
  }
  if(dimension == 'height'){
    return window.innerHeight ? window.innerHeight : $(window).height();
  }
}


var month=[];
month[0]="Jan";
month[1]="Feb";
month[2]="Mar";
month[3]="Apr";
month[4]="May";
month[5]="Jun";
month[6]="Jul";
month[7]="Aug";
month[8]="Sep";
month[9]="Oct";
month[10]="Nov";
month[11]="Dec";


//Need this because Safari can't handle iso8601 with the JS Date.parse function - all other browsers work though
//Options
//parseDate('06.21.2010', 'mm.dd.yyyy');
//parseDate('21.06.2010', 'dd.mm.yyyy');
//parseDate('2010/06/21', 'yyyy/mm/dd');
//parseDate('2010-06-21');

function parseDate(input, format) {
  if(typeof input !== "undefined" && input.length) {
    format = format || 'yyyy-mm-dd'; // default format
    var parts = input.match(/(\d+)/g),
        i = 0, fmt = {};
    // extract date-part indexes from the format
    format.replace(/(yyyy|dd|mm)/g, function(part) { fmt[part] = i++; });

    //return Date.UTC(parts[fmt['yyyy']], parts[fmt['mm']]-1, parts[fmt['dd']]);
    return Date.parse(month[parseInt(parts[fmt['mm']]-1, 10)] + ' ' + parts[fmt['dd']] + ', ' + parts[fmt['yyyy']]);
  }
}


function ISODateString(d){
 function pad(n){return n<10 ? '0'+n : n;}
 return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate());
}


function date_by_subtracting_days(date, days) {
    return new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate() - days,
        date.getHours(),
        date.getMinutes(),
        date.getSeconds(),
        date.getMilliseconds()
    );
}



//Function for changing the marker types on the main map when user clicks one of the buttons at bottom right of map
function changeMapMarker(dataType){
  markerType = dataType;
  mapType = $('#map_canvas').gmap('getType');

  if(getScreenSize('height') > getScreenSize('width')){
    legendWidth = "275";
    infoPopupWidth = "200";
    infoPopupHeight = "200";
  }
  else{
    legendWidth = "400";
    infoPopupWidth = "370";
    infoPopupHeight = "130";
  }

  $('#map_canvas').gmap('clearControl',google.maps.ControlPosition.RIGHT_BOTTOM); //Clearing prevents position migration downwards
  legendMain = new Legend("Legend", "80px", legendContentHtml[dataType], legendWidth+'px'); //Redefine legend text for new marker type

  $('#map_canvas').gmap('clear', 'markers');

  populateMarkers(false); //false refers to not setting the map zoom to the marker bounds - this prevents re-zooming/centering of the map when changing the marker type
  mapUserMarker();

  $('#markerTypeSelector').trigger('create'); //Applies JQM styling to the markerTypeSelector radio buttons
}


//Functions for geolocating user and displaying them on the map - need to consolidate extra "detail" map code into main function
var markerMapped;

function mapUserMarker(){
  var clientPosition = new google.maps.LatLng(userLat, userLng);
  $('#map_canvas').gmap('addMarker', {'position': clientPosition, 'icon': 'static/images/blue_dot_circle.png', 'bounds': false});
  markerMapped = 1;

  if((userLat > 33.501 && userLat < 33.880) && (userLng > -79.067 && userLng < -78.511)){ //Check if user is in the area and if so, zoom in to their location
    $('#map_canvas').gmap('option', 'zoom', 11);
    $('#map_canvas').gmap('option', 'center', new google.maps.LatLng(userLat,userLng));
    $('#map_canvas').gmap('refresh');
  }

}


function initializeGeoDetail() {
  if (navigator.geolocation) {

    navigator.geolocation.getCurrentPosition(
      onSuccessDetail);
  }
  else {
    alert('Geolocation not supported.');
  }
}

function onSuccessDetail(position) {
  userLat = position.coords.latitude;
  userLng = position.coords.longitude;

  var clientPosition = new google.maps.LatLng(userLat, userLng);
  $('#detail_map_canvas').gmap('addMarker', {'position': clientPosition, 'icon': 'static/images/blue_dot_circle.png', 'bounds': false});
}



function onLocationSuccess(position) {
  userLat = position.coords.latitude;
  userLng = position.coords.longitude;
  //userLat = 33.726856; //fake user lat for testing
  //userLng = -78.927974; //fake user lng for testing

  if ($("#beachListPage").is(".ui-page-active")){
    $('#beachListPage').trigger('pageinit');
  }

  if ($("#mapPage").is(".ui-page-active")){
    mapUserMarker();
  }
}



function getUserLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      onLocationSuccess);
  }
  else {
    alert('Geolocation not supported.');
  }
}


document.addEventListener("deviceready", function(){

    function onDeviceReady() {
      StatusBar.hide();
    }

    //navigator.geolocation.getCurrentPosition(onsuccess, onerror, params);
    getUserLocation();
    navigator.splashscreen.hide();
}, false);






//Redirect to Offline page on pageshow if internet is not available
$('[data-role="page"]').on('pageshow', function () {
  if(onlineStatus == 'off') $.mobile.pageContainer.pagecontainer('change', '#offlineMessage');
});


waitUntilExists("markerTypeSelector",function(){
  $('#markerTypeSelector').trigger('create'); //Applies JQM styling to the markerTypeSelector radio buttons
});

waitUntilExists("homeResetButton",function(){
  $('#homeResetButton').trigger('create'); //Applies JQM styling to the home reset button
});


$(window).bind('orientationchange', function(e) {
  //alert('orientationchange: '+e.orientation);
  $(window).trigger('resize');
});

$(window).bind('resize', function(e) {
  if ($("#beachDetailsPage").is(".ui-page-active")){
    $('#beachDetailsPage').trigger('pageshow');
  }
  if ($("#mapPage").is(".ui-page-active")){
    $('#mapPage').trigger('pageshow');

    //alert('H:'+getScreenSize('height')+' W:'+getScreenSize('width'));
    //if(e.orientation == 'portrait'){
    if(getScreenSize('height') > getScreenSize('width')){
      legendWidth = "275";
      infoPopupWidth = "200";
      infoPopupHeight = "200";
    }
    else{
      legendWidth = "400";
      infoPopupWidth = "370";
      infoPopupHeight = "130";
    }

    $('#legend').width(legendWidth);
    $('#map_canvas').gmap('closeInfoWindow'); //close it because it will have the wrong dimensions for new screen orientation

  }
});

// Apply loading spinner for all clicks accept those with 'noloader' class
$('a:not(.noloader)').on('click', function() {
  $(window).bind('hashchange', function() {
    $('body').addClass('ui-loading');
  });
});


//Retrieve the GET parameters - used for beach details page - makes use of the jqm.page.params.js script
$(document).bind("pagebeforechange", function( event, data ) {
  $.mobile.pageData = (data && data.options && data.options.pageData) ? data.options.pageData : null;
});


//Populate predictionData array with needed parameters for all stations.
//Using $.ajax and async: false, rather than $.getJSON to ensure that predictionData is populated before pages try to use it.

/*
var predictionData = {};
var popupMessage;

$.ajax({
    type: "GET",
    cache : false,
    async: false,
    crossDomain: false,
    timeout: 5000,
    //url: "http://howsthebeach.org/ba-simple-proxy.php?url=http://129.252.139.124/mapping/xenia/feeds/florida_wq/Predictions.json",
    //url: "http://dev.howsthebeach.org/rest/sarasota/predictions/current_results",
    //url: site_base_url + "predictions/current_results",
    url: "/predictions/current_results/" + site,
    dataType: "json",
    success: function(data) {
      $.each( data, function(i, contents) {
        if(contents.message != '') popupMessage = contents.message;
      });
      var forecast_date = data.contents.testDate;

      $.each( data.contents.stationData.features, function(i, beach) {
        predictionData[beach.properties.station] = {
          "station" : beach.properties.station,
          "desc" : beach.properties.desc,
          "ensemble" : beach.properties.ensemble,
          "forecast_date": forecast_date,
          "message" : beach.properties.message,
          "region" : beach.properties.region,
          "lat" : beach.geometry.coordinates[1],
          "lng" : beach.geometry.coordinates[0] };
      });

      console.log('PD:'+predictionData);
    },
    error: function (xhr, ajaxOptions, thrownError) {
      onlineStatus = 'off';
      //alert(xhr.status);
      //alert(thrownError);
    }
});
*/
//Get monitoring data and populate currentEtcoc array for all stations
//Using $.ajax and async: false, rather than $.getJSON to ensure that currentEtcoc is populated before pages try to use it.

if(onlineStatus != 'off'){

  function calcDataRating(etcoc, station_data) {
    var rating = 'none';
    //var station_sample_date = station_data.date;
    //var advisory = station_data.advisory;
    var station_sample_date = station_data.SampleDate();
    var advisory = station_data.SampleStationMessage();

    if(advisory=='Yes' || advisory=='Long Term')
    {
      rating = 'high';
    }
    else {
      if (station_sample_date !== undefined && station_sample_date.length) {
        var sampleDate = parseDate(station_sample_date);

        sampleDate = new Date(sampleDate);

        //remove > and < for calculating color
        if (typeof etcoc !== 'undefined') {
          //DWR 2015-12-10
          //Verify that the etcoc is a string.
          if (typeof etcoc === "string") {
            etcoc = etcoc.replace('>', '').replace('<', '');
          }
        }

        if (etcoc == 'None' || days_between(new Date(), sampleDate) > 30) {
          rating = 'none';
        }
        else if((isNaN(etcoc) || etcoc <= advisory_limits['Low'].max_limit) ||
          (etcoc > advisory_limits['Low'].max_limit && etcoc <= advisory_limits['Medium'].max_limit))
        {
          rating = 'low';
        }
        /*
        else if (etcoc > advisory_limits['Low'].max_limit && etcoc <= advisory_limits['Medium'].max_limit) {
          rating = 'medium';
        }
        */
        else {
          rating = 'high';
        }
      }
    }
    return  rating;
  }

  function calcAdvisoryRating(station){
    var rating = 'none';
    //var advisory = station.advisory;
    var advisory = station.SampleStationMessage();
    if(advisory == 'Long Term')
    {
      rating = 'high';
    }
    else
    {
      //if(station.date.length) {
      if(station.SampleDate() !== undefined && station.SampleDate().length) {
        var date = station.SampleDate();
        var data_age_days = days_between(new Date(), new Date(date));
        if (data_age_days > 30) {
          rating = 'none';
        }
        else {
          if (advisory == 'Yes') {
            rating = 'high';
          }
          else {
            rating = 'low';
          }
        }
      }
    }
    return rating;

  }
  function get_bacteria_style(station, etcoc)
  {
    var css_class = 'popup_label_none';
    //var station_sample_date = station.date;
    var station_sample_date = station.SampleDate();

    if (station_sample_date !== undefined && station_sample_date.length)
    {
      var sampleDate = parseDate(station_sample_date);

      sampleDate = new Date(sampleDate);

      //remove > and < for calculating color
      if (typeof etcoc !== 'undefined') {
        if (typeof etcoc === "string") {
          etcoc = etcoc.replace('>', '').replace('<', '');
        }
      }

      if (etcoc == 'None' || days_between(new Date(), sampleDate) > 30) {
        css_class = 'popup_label_none';
      }
      else if (isNaN(etcoc) || etcoc <= advisory_limits['Low'].max_limit) {
        css_class = 'popup_label_low';
      }
      else if (etcoc > advisory_limits['Low'].max_limit && etcoc <= advisory_limits['Medium'].max_limit) {
        css_class = 'popup_label_medium';
      }
      else {
        css_class = 'popup_label_high';
      }
    }

    return(css_class);
  }
  function get_advisory_style(station)
  {
    var css_class = 'popup_label_none';
    //var advisory = station.advisory;
    var advisory = station.SampleStationMessage();
    if(advisory == 'Long Term')
    {
      css_class = 'popup_label_high';
    }
    else
    {
      //if(station.date.length) {
      if(station.SampleDate() !== undefined && station.SampleDate().length) {
        //var date = station.date;
        var date = station.SampleDate();
        var data_age_days = days_between(new Date(), new Date(date));
        if (data_age_days > 30) {
          css_class = 'popup_label_nodata';
        }
        else {
          if (advisory == 'Yes') {
            css_class = 'popup_label_high';
          }
          else {
            css_class = 'popup_label_low';
          }
        }
      }
    }
    return css_class;
  }

  //Map legend setup
  function Legend(name, controlWidth, content, contentWidth) {
    this.name = name;
    this.content = content;

    var container = document.createElement("div");
    container.style.position = "relative";
    container.style.margin = "0 10px 5px 5px";
    container.style.zIndex = "9999999999999999999999999";

    var legendButtonHtml = '<div style="padding:3px" class="ui-btn ui-input-btn ui-corner-all ui-mini">' +

                   name +

               '</div>' +
               '<div id="legend" class="legend" style="display: none;width: ' + contentWidth + '">' +
               '<div id="legend_close" style="width: 18px; height: 18px; overflow: hidden; position: absolute; opacity: 0.7; right: 12px; top: 12px; z-index: 10000; cursor: pointer;"><img src="http://maps.gstatic.com/mapfiles/api-3/images/mapcnt3.png" draggable="false" style="position: absolute; left: -2px; top: -336px; width: 59px; height: 492px; -webkit-user-select: none; border: 0px; padding: 0px; margin: 0px;"></div>' +
                 content +
               '</div>';

    container.innerHTML = legendButtonHtml;
    this.div = container;

    var control = container.childNodes[0];
    var legend  = container.childNodes[1];
    var legendCloseButton = container.childNodes[1].childNodes[0];

    control.onclick = toggle;
    legendCloseButton.onclick = toggle;


    function toggle() {
      if (legend.style.display == "none") {
        legend.style.display = "block";
      } else {
        legend.style.display = "none";
      }
    }
  }

  if(getScreenSize('height') > getScreenSize('width')){
    legendWidth = "275";
    infoPopupWidth = "200";
    infoPopupHeight = "200";
  }
  else{
    legendWidth = "400";
    infoPopupWidth = "370";
    infoPopupHeight = "130";
  }

  var legendContentHtml = [];

  legendContentHtml['forecast'] = '<div><p><strong>Today\'s forecasted conditions</strong></p><div style="float:left;padding-right:10px;"><img src="static/images/none_marker.png" /> No forecast available<br /><img src="static/images/low_marker.png" /> Low bacteria level</div><div style="float:left"><img src="static/images/medium_marker.png" /> Medium bacteria level<br /><img src="static/images/high_marker.png" /> High bacteria level</div><br style="clear:both"><a class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-corners="true" href="#moreInformation" data-role="button" data-mini="true" style="padding:0.4em 1em;"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Info</span></span></a></div>';
  legendContentHtml['advisories'] = '<div><p><strong>Swim advisories</strong></p><p><img src="static/images/low_marker.png" /> None: no swimming advisory issued - safe to swim.<br /><img src="static/images/high_marker.png" /> Yes: an advisory is current - swimming not recommended.</br><img src="static/images/none_marker.png" />No data available or data older than 30 days.<br /></p><a class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-corners="true" href="#moreInformation" data-role="button" data-mini="true" style="padding:0.4em 1em;"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Info</span></span></a></div>';
  legendContentHtml['data'] = '<div><p><strong>Bacteria level data</strong></p><div style="float:left;padding-right:10px;"><img src="static/images/none_marker.png" /> No data available<br /><img src="static/images/low_marker.png" /> Low bacteria level</div><div style="float:left"><img src="static/images/medium_marker.png" /> Medium bacteria level<br /><img src="static/images/high_marker.png" /> High bacteria level</div><br style="clear:both"><a class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-corners="true" href="#moreInformation" data-role="button" data-mini="true" style="padding:0.4em 1em;"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Info</span></span></a></div>';

  var legendMain = new Legend("Legend", "80px", legendContentHtml[markerType], legendWidth+'px');
  var legendDetail = new Legend("Legend", "80px", legendContentHtml[markerType], legendWidth+'px');


  function resetHome(zoom, center){
    $('#map_canvas').gmap('option', 'center', center);
    $('#map_canvas').gmap('option', 'zoom', zoom);
  }


  //Home/reset button setup
  function Button(name) {

    var content = '<input type="button" data-mini="true" data-role="button" name="home" id="home" data-icon="home" data-iconpos="notext" onclick="resetHome(initialZoom,initialCenter);" />';

    this.name = name;
    this.content = content;

    var container = document.createElement("div");
    container.id = "homeResetButton";
    container.style.position = "relative";
    container.style.margin = "0 0 0 5px";
    container.style.padding = "3px";
    container.innerHTML = content;
    this.div = container;

  }

  var homeButton = new Button("Home");


  function add_default_site_marker(i, station, bounds)
  {
      var forecast = 'None';
      var station_message = '';
      var sample_value = 'None';
      //Map markers
      if (typeof station.EnsembleResult() === "undefined" || station.EnsembleResult() == "NO TEST") {
        forecast = 'None';
      }
      else {
        forecast = station.EnsembleResult();
      }

      if (typeof station.ForecastStationMessage() !== 'undefined') {
        station_message = station.ForecastStationMessage();
      }
      else {
        station_message = '';
      }
      var dateIcon = '';
      var sample_date = '';
      if (station.SampleDate() === undefined || station.SampleDate().length === 0) {
        dateIcon = '';
      }
      else {
        sample_date = new Date(parseDate(station.SampleDate()));
        dateIcon = ' (' + sample_date.getDate() + ' ' + month[sample_date.getMonth()] + ' \'' + sample_date.getFullYear().toString().substr(2, 2) + ')';
        sample_value = station.SampleValue();
      }

      if (markerType == 'forecast') {
        markerRating = forecast;
      }

      if (markerType == 'advisories') {
        markerRating = calcDataRating(sample_value, station);

      }
      //https://developers.google.com/maps/documentation/javascript/reference#MapTypeControlStyle for options to disable other elements on the map
      var myStyles = [
        {
          featureType: "poi",
          elementType: "labels",
          stylers: [
            {visibility: "off"}
          ]
        }
      ];

      $('#map_canvas').gmap('option', 'mapTypeId', google.maps.MapTypeId.MAP);
      $('#map_canvas').gmap('option', 'styles', myStyles);
      $('#map_canvas').gmap('option', 'disableDefaultUI', true); //disable all controls then add in what we want
      $('#map_canvas').gmap('option', 'mapTypeControl', true);
      $('#map_canvas').gmap('option', 'streetViewControl', true);
      $('#map_canvas').gmap('option', 'mapTypeControlOptions', {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU});

      var site_location = station.Location();
      $('#map_canvas').gmap('addMarker', {
        'position': new google.maps.LatLng(site_location[1], site_location[0]),
        'icon': 'static/images/' + markerRating.toLowerCase() + '_marker.png',
        'bounds': bounds
      }).click(function () {
        //var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.desc + '</strong>'];
        var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.Description() + '</strong>'];
        popup_content.push('<div>');
        popup_content.push('<div style="float:left;padding-right:20px;padding-top:15px;"><div style="text-align:right">Forecast (' + new Date().getDate() + ' ' + month[new Date().getMonth()] + ')&nbsp;&nbsp;&nbsp;<span class="popup_label_' + forecast.toLowerCase().replace(' ', '') + '">' + capitalize(forecast) + '</span></div></div>');
        //If the station does not issue advisories, do not add the field. A station
        //may collect data but advisories not issued by the governmental agency.
        //if(station.issues_advisories) {
        if(station.IssuesAdvisories()) {
          //popup_content.push('<div style="float:left;padding-top:15px;"><div style="text-align:right">Advisory&nbsp;&nbsp;&nbsp;<span class="' + get_advisory_style(station) + '">' + station.advisory.replace("<br />", " ") + '</span></div></div><br style="clear:both">')
          popup_content.push('<div style="float:left;padding-top:15px;"><div style="text-align:right">Advisory&nbsp;&nbsp;&nbsp;<span class="' + get_advisory_style(station) + '">' + station.SampleStationMessage().replace("<br />", " ") + '</span></div></div><br style="clear:both">')
        }
        popup_content.push('<div style="float:left;padding-right:20px;padding-top:15px;"><div style="text-align:right">Bacteria Data' + dateIcon + '&nbsp;&nbsp;&nbsp;<span class="' + get_bacteria_style(station, sample_value) +'">' + sample_value + '</span></div></div>')
        popup_content.push('<div style="float:left;padding-left:30px;"><div><a style="float:right;margin:10px 0;padding:6px 12px 3px 12px;" class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-history="false" data-corners="true" href="#beachDetailsPage?id=' + i + '" data-role="button" data-icon="info" data-mini="true"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Details</span><span class="ui-icon ui-icon-info ui-icon-shadow">&nbsp;</span></span></a></div></div>');
        popup_content.push('<div style="clear:both;white-space:normal;">' + station_message + '</div>');
        popup_content.push('</div>');
        popup_content.push('</div>');
        $('#map_canvas').gmap('openInfoWindow', {
          'content': popup_content.join('')
        },
        this);
        //SEnd google analytic event that reflects the station the user clicked on.
        ga('send', {
          hitType: 'event',
          eventCategory: 'SampleSiteClick',
          eventAction: 'click',
          eventLabel: station.Station()
        });

      });
  };
  function add_camera_site(i, station, bounds)
  {

      var site_location = station.Location();
      $('#map_canvas').gmap('addMarker', {
        'position': new google.maps.LatLng(site_location[1], site_location[0]),
        'icon': 'static/images/webcam_icon.png',
        'bounds': bounds
      }).click(function () {
        var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.Description() + '</strong>'];
        popup_content.push('<div>');
        var camera_page = site + '/camera/' + i;
        popup_content.push('<div style="float:left;padding-left:30px;"><div><a style="float:right;margin:10px 0;padding:6px 12px 3px 12px;" class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-history="false" data-corners="true" href="'+camera_page+'" data-role="button" data-icon="info" data-mini="true"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Details</span><span class="ui-icon ui-icon-info ui-icon-shadow">&nbsp;</span></span></a></div></div>');

        $('#map_canvas').gmap('openInfoWindow',
            {
              'content': popup_content.join('')
            }, this);
        //SEnd google analytic event that reflects the station the user clicked on.
        ga('send', {
          hitType: 'event',
          eventCategory: 'SampleSiteClick',
          eventAction: 'click',
          eventLabel: station.Station()
        });

      });

  };
  function add_camera_site(i, station, bounds)
  {

      var site_location = station.Location();
      $('#map_canvas').gmap('addMarker', {
        'position': new google.maps.LatLng(site_location[1], site_location[0]),
        'icon': 'static/images/shell_open.png',
        'bounds': bounds
      }).click(function () {
        var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.Description() + '</strong>'];
        //popup_content.push('<div>');
        //var camera_page = site + '/camera/' + i;
        popup_content.push('<div style="float:left;padding-left:30px;"><div><a style="float:right;margin:10px 0;padding:6px 12px 3px 12px;" class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-history="false" data-corners="true" href="'+camera_page+'" target="_top" data-role="button" data-icon="info" data-mini="true"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Details</span><span class="ui-icon ui-icon-info ui-icon-shadow">&nbsp;</span></span></a></div></div>');

        $('#map_canvas').gmap('openInfoWindow',
            {
              'content': popup_content.join('')
            }, this);
        //SEnd google analytic event that reflects the station the user clicked on.
        ga('send', {
          hitType: 'event',
          eventCategory: 'SampleSiteClick',
          eventAction: 'click',
          eventLabel: station.Station()
        });

      });

  };
  //Function for populating main overview map with markers
  function populateMarkers(bounds){

      //$.each( currentEtcoc, function(i, station) {
      $.each( stations_records.station_data_records, function(i, station) {
        if(station.SiteType() == undefined || station.SiteType() == "Default")
        {
          add_default_site_marker(i, station, bounds);
        }
        else if(station.SiteType() == "Camera Site")
        {
          add_camera_site(i, station, bounds);
        }
        else if(station.SiteType() == "Shellfish")
        {

        }
        /*
        var forecast = 'None';
        var station_message = '';
        var sample_value = 'None';
        //Map markers
        if (typeof station.EnsembleResult() === "undefined" || station.EnsembleResult() == "NO TEST") {
          forecast = 'None';
        }
        else {
          forecast = station.EnsembleResult();
        }

        if (typeof station.ForecastStationMessage() !== 'undefined') {
          station_message = station.ForecastStationMessage();
        }
        else {
          station_message = '';
        }
        var dateIcon = '';
        var sample_date = '';
        if (station.SampleDate() === undefined || station.SampleDate().length === 0) {
          dateIcon = '';
        }
        else {
          sample_date = new Date(parseDate(station.SampleDate()));
          dateIcon = ' (' + sample_date.getDate() + ' ' + month[sample_date.getMonth()] + ' \'' + sample_date.getFullYear().toString().substr(2, 2) + ')';
          sample_value = station.SampleValue();
        }

        if (markerType == 'forecast') {
          markerRating = forecast;
        }

        if (markerType == 'advisories') {
          markerRating = calcDataRating(sample_value, station);

        }
        //https://developers.google.com/maps/documentation/javascript/reference#MapTypeControlStyle for options to disable other elements on the map
        var myStyles = [
          {
            featureType: "poi",
            elementType: "labels",
            stylers: [
              {visibility: "off"}
            ]
          }
        ];

        $('#map_canvas').gmap('option', 'mapTypeId', google.maps.MapTypeId.MAP);
        $('#map_canvas').gmap('option', 'styles', myStyles);
        $('#map_canvas').gmap('option', 'disableDefaultUI', true); //disable all controls then add in what we want
        $('#map_canvas').gmap('option', 'mapTypeControl', true);
        $('#map_canvas').gmap('option', 'streetViewControl', true);
        $('#map_canvas').gmap('option', 'mapTypeControlOptions', {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU});

        var site_location = station.Location();
        $('#map_canvas').gmap('addMarker', {
          'position': new google.maps.LatLng(site_location[1], site_location[0]),
          'icon': 'static/images/' + markerRating.toLowerCase() + '_marker.png',
          'bounds': bounds
        }).click(function () {
          //var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.desc + '</strong>'];
          var popup_content = ['<div id="infoPopup" style="width:' + infoPopupWidth + 'px;height:' + infoPopupHeight + 'px;clear:both;white-space:nowrap;line-height:normal;"><strong>' + station.Description() + '</strong>'];
          popup_content.push('<div>');
          popup_content.push('<div style="float:left;padding-right:20px;padding-top:15px;"><div style="text-align:right">Forecast (' + new Date().getDate() + ' ' + month[new Date().getMonth()] + ')&nbsp;&nbsp;&nbsp;<span class="popup_label_' + forecast.toLowerCase().replace(' ', '') + '">' + capitalize(forecast) + '</span></div></div>');
          //If the station does not issue advisories, do not add the field. A station
          //may collect data but advisories not issued by the governmental agency.
          //if(station.issues_advisories) {
          if(station.IssuesAdvisories()) {
            //popup_content.push('<div style="float:left;padding-top:15px;"><div style="text-align:right">Advisory&nbsp;&nbsp;&nbsp;<span class="' + get_advisory_style(station) + '">' + station.advisory.replace("<br />", " ") + '</span></div></div><br style="clear:both">')
            popup_content.push('<div style="float:left;padding-top:15px;"><div style="text-align:right">Advisory&nbsp;&nbsp;&nbsp;<span class="' + get_advisory_style(station) + '">' + station.SampleStationMessage().replace("<br />", " ") + '</span></div></div><br style="clear:both">')
          }
          popup_content.push('<div style="float:left;padding-right:20px;padding-top:15px;"><div style="text-align:right">Bacteria Data' + dateIcon + '&nbsp;&nbsp;&nbsp;<span class="' + get_bacteria_style(station, sample_value) +'">' + sample_value + '</span></div></div>')
          popup_content.push('<div style="float:left;padding-left:30px;"><div><a style="float:right;margin:10px 0;padding:6px 12px 3px 12px;" class="ui-btn ui-btn-corner-all ui-mini ui-btn-up-c" data-theme="c" data-wrapperels="span" data-history="false" data-corners="true" href="#beachDetailsPage?id=' + i + '" data-role="button" data-icon="info" data-mini="true"><span class="ui-btn-inner ui-btn-corner-all"><span class="ui-btn-text">More Details</span><span class="ui-icon ui-icon-info ui-icon-shadow">&nbsp;</span></span></a></div></div>');
          popup_content.push('<div style="clear:both;white-space:normal;">' + station_message + '</div>');
          popup_content.push('</div>');
          popup_content.push('</div>');
          $('#map_canvas').gmap('openInfoWindow', {
            'content': popup_content.join('')
          },
          this);
          //SEnd google analytic event that reflects the station the user clicked on.
          ga('send', {
            hitType: 'event',
            eventCategory: 'SampleSiteClick',
            eventAction: 'click',
            eventLabel: station.Station()
          });

        });
      //}
      */});
    //Add legend back in with text for new marker type
    $('#map_canvas').gmap('addControl', legendMain.div, google.maps.ControlPosition.RIGHT_BOTTOM);
  }


  //Set up the main overview map
  var initialZoom;
  var initialCenter;

  $('#mapPage').bind('pageinit', function(event) {
    populateMarkers('true'); //true refers to setting the map zoom to the marker bounds

    $('#map_canvas').gmap('addControl', homeButton.div, google.maps.ControlPosition.TOP_LEFT);
    $('#markerTypeSelector').trigger('create'); //Applies JQM styling to the markerTypeSelector radio buttons
  });



  $('#mapPage').bind('pageshow', function(event) {

    var mapHeight = getScreenSize('height') - (document.getElementById('mainheader').offsetHeight) - (document.getElementById('mainfooter').offsetHeight) + 2;
    //var mapHeight = getScreenSize('height') - (document.getElementById('mainheader').offsetHeight*2)+2;

    $('#map_canvas').css( "height", mapHeight );

    if(markerMapped!==1){
      if(typeof userLat !== 'undefined'){
        mapUserMarker();
      }
      else{
        getUserLocation();
      }
    }

    //This repositions the map in case the user reloaded on the search or info pages - hence the zoom defaults to world level = 2
    if($('#map_canvas').gmap('getZoom') <= 2){
      $('#map_canvas').gmap('fitbounds');
      //Increase zoom one level on smaller phones
      if(getScreenSize('height') < 500){
        $('#map_canvas').gmap('option', 'zoom', ($('#map_canvas').gmap('getZoom')+1));
      }
      $('#map_canvas').gmap('refresh');
    }

    $('#markerTypeSelector').trigger('create'); //Applies JQM styling to the markerTypeSelector radio buttons

    $('#map_canvas').gmap('refreshZoom');

    $('body').removeClass('ui-loading');


    //if(popupMessage != '') alert(popupMessage);
  });


  $('#map_canvas').gmap().bind('init', function(event, map) {
    initialZoom = $('#map_canvas').gmap('getZoom');
    initialCenter = $('#map_canvas').gmap('getCenter');

    //Increase zoom one level on smaller phones
    if(getScreenSize('height') < 500){
      $('#map_canvas').gmap('option', 'zoom', (initialZoom+1));
      $('#map_canvas').gmap('refreshZoom');
    }
  });


  //Populates the List page with all the beaches and their current forecast, latest monitoring ETCOC, and advisory status

  //Function to sort list columns onclick in alternate directions
  var aAsc = [];
  function sortBy(column){
    aAsc[column] = aAsc[column]=='asc'?'desc':'asc';
    $('ul#beachList>li').tsort('span:eq('+column+')',{attr:'id', order:aAsc[column]});
    $('#arrows_1').removeClass('arrow-asc');
    $('#arrows_3').removeClass('arrow-asc');
    $('#arrows_4').removeClass('arrow-asc');
    $('#arrows_5').removeClass('arrow-asc');
    $('#arrows_1').removeClass('arrow-desc');
    $('#arrows_3').removeClass('arrow-desc');
    $('#arrows_4').removeClass('arrow-desc');
    $('#arrows_5').removeClass('arrow-desc');
    $('#arrows_'+column).addClass('arrow-'+aAsc[column]);

    $('#beachList').listview('refresh');
  }

  // Deals with converting low, medium, high into something we can sort
  function numerizeForecast(forecast){
    if(forecast == 'Low'){
      return 1;
    }
    if(forecast == 'Medium'){
      return 2;
    }
    if(forecast == 'High'){
      return 3;
    }
    if(forecast == 'None'){
      return 4;
    }

  }


  function numerizeAdvisory(advisory){
    if(advisory == 'None'){
      return 1;
    }
    if(advisory == 'Yes'){
      return 2;
    }
  }


  function numerizeNone(data){
    if(data == 'None'){
      return 99999999999; //force no data to end of sort
    }
    else {
      if(typeof data !== 'undefined') {
        //DWR 2015-12-10
        //Verify that the etcoc is a string.
        if (typeof data === "string") {
          return data.replace('>', '').replace('<', '');
        }
      }
    }

    /*
    if(data == 'None'){
      return 99999999999; //force no data to end of sort
    }
    else{
      return data.replace('>','').replace('<','');
    }*/
  }

  $('#beachListPage').bind('pageinit', function(event) {

    if(typeof dateSet === 'undefined'){
      $( "#forecast_column" ).append(' ('+new Date().getDate()+' '+month[new Date().getMonth()]+')');
      dateSet = 1;
    }

    $('#beachList li').remove();
    var currentSection;

    //$.each(currentEtcoc, function(i,station){
    $.each( stations_records.station_data_records, function(i, station) {
      var sample_value = 'None';
      //if(typeof predictionData[i] === "undefined" || predictionData[i].ensemble == "NO TEST"){
      if(station.EnsembleResult() === undefined || station.EnsembleResult() == "NO TEST"){
        var forecast = 'None';
      }
      else{
        var forecast = station.EnsembleResult();
      }

      var dateIcon = '';

      //if(typeof station.date === "undefined" || station.date.length === 0){
      if(station.SampleDate() === undefined || station.SampleDate().length === 0){
        dateIcon = '<span>&nbsp;</span>'; //need to keep number of spans consistent which is important for column sorting and was being affected if no data available and hence no date span being displayed
      }
      else{
        //var sample_date = new Date(parseDate(station.date));
        var sample_date = new Date(parseDate(station.SampleDate()));
        dateIcon = ' ('+sample_date.getDate()+'&nbsp;'+month[sample_date.getMonth()]+' \''+sample_date.getFullYear().toString().substr(2,2)+')';
        //dateIcon = ' ('+new Date(parseDate(station.date)).getDate()+'&nbsp;'+month[new Date(parseDate(station.date)).getMonth()]+' \''+new Date(parseDate(station.date)).getFullYear().toString().substr(2,2)+')';
        sample_value = station.SampleValue();
      }

      if(typeof userLat !== 'undefined'){
        var site_location = station.Location();
        distance = calcDistance(userLat,userLng,site_location[1],site_location[0])*0.621371;
        if(distance <100){
          round = 2;
        }
        else if(distance >=100 && distance <1000){
          round = 1;
        }
        else{
          round = 0;
        }
        distance = Math.roundTo(distance,round);
        distanceUnits = ' miles';
      }
      else{
        distance = '';
        distanceUnits = '';
      }

      //$('#beachList').append('<li data-theme="d" style="padding:0" data-icon="false" data-filtertext="' + forecast + ' ' + i + ' ' + station.region + ' ' + station.desc + '"><a style="text-decoration:none;padding:2px 2px 2px 5px;" href="#beachDetailsPage?id=' + i + '"><span class="rating-name" style="text-align:left">' + $.trim(station.desc).replace(/\(.*?\)/g, '').replace(/^(.{23}[^\s]*).*/, "$1") +'<br /><span id="' + distance + '" style="font-weight:normal">' + distance + '</span><span style="font-weight:normal">' + distanceUnits + '</span></span><span id="' + numerizeForecast(capitalize(forecast)) + '" class="'+forecast.toLowerCase().replace(' ','')+' rating">' + capitalize(forecast) + '</span><span id="' + numerizeAdvisory(station.advisory) + '" class="' +calcAdvisoryRating(station)+ ' rating" style="width:23.5%">'+station.advisory+'</span><span id="' + numerizeNone(data) + '" class="'+calcDataRating(data, station)+' rating">'+data+'<br />'+dateIcon+'</span></a></li>');
      $('#beachList').append('<li data-theme="d" style="padding:0" data-icon="false" data-filtertext="' + forecast + ' ' + i + ' ' + station.Region() + ' ' + station.Description() + '"><a style="text-decoration:none;padding:2px 2px 2px 5px;" href="#beachDetailsPage?id=' + i + '"><span class="rating-name" style="text-align:left">' + $.trim(station.Description()).replace(/\(.*?\)/g, '').replace(/^(.{23}[^\s]*).*/, "$1") +'<br /><span id="' + distance + '" style="font-weight:normal">' + distance + '</span><span style="font-weight:normal">' + distanceUnits + '</span></span><span id="' + numerizeForecast(capitalize(forecast)) + '" class="'+forecast.toLowerCase().replace(' ','')+' rating">' + capitalize(forecast) + '</span><span id="' + numerizeAdvisory(station.SampleStationMessage()) + '" class="' +calcAdvisoryRating(station)+ ' rating" style="width:23.5%">'+station.SampleStationMessage()+'</span><span id="' + numerizeNone(sample_value) + '" class="'+calcDataRating(sample_value, station)+' rating">'+sample_value+'<br />'+dateIcon+'</span></a></li>');

    });

    $('#beachList').append('<li>&nbsp;</li>');
    $('ul#beachList>li').tsort('span:eq(1)');//sort by the second span, which is distance from the user's location
    $('#beachList').listview('refresh');

  });


  $('#beachListPage').bind('pageshow', function(event) {
    $('body').removeClass('ui-loading');
  });


  $('#moreInformation').bind('pageshow', function(event) {
    $('body').removeClass('ui-loading');
  });

  $('#offlineMessage').bind('pageshow', function(event) {
    $('body').removeClass('ui-loading');
  });



  //Populates the beach details page with map and graph tabs
  var options;
  var monitoringChart;

  $('#beachDetailsPage').bind('pageinit', function(event) {

    $( "#details_forecast_column" ).append(' ('+new Date().getDate()+' '+month[new Date().getMonth()]+')');

    var station = stations_records.StationData($.mobile.pageData.id)
    //if(currentEtcoc[$.mobile.pageData.id].date.length == 0 || typeof currentEtcoc[$.mobile.pageData.id].date === "undefined"){
    var sample_date = station.SampleDate();
    if(sample_date === undefined || sample_date.length == 0 ){
      $( "#details_data_column" ).append('<span>&nbsp;</span>'); //need to keep number of spans consistent - maybe not necessary here like it is on the beach list page
    }
    else{
      //$( "#details_data_column" ).append(' ('+new Date(parseDate(currentEtcoc[$.mobile.pageData.id].date)).getDate()+' '+month[new Date(parseDate(currentEtcoc[$.mobile.pageData.id].date)).getMonth()]+' \''+new Date(parseDate(currentEtcoc[$.mobile.pageData.id].date)).getFullYear().toString().substr(2,2)+')');
      $( "#details_data_column" ).append(' ('+new Date(parseDate(sample_date)).getDate()+' '+month[new Date(parseDate(sample_date)).getMonth()]+' \''+new Date(parseDate(sample_date)).getFullYear().toString().substr(2,2)+')');
    }

    dateSet = 1;


    //Legend needs to be set up on pageinit or it duplicates, or is positioned further down the page
    $('#detail_map_canvas').gmap('addControl', legendDetail.div, google.maps.ControlPosition.RIGHT_BOTTOM);

    $('#detail_map_canvas').gmap('option', 'mapTypeId', google.maps.MapTypeId.HYBRID);
    $('#detail_map_canvas').gmap('option', 'disableDefaultUI', true); //disable all controls then add in what we want
    $('#detail_map_canvas').gmap('option', 'mapTypeControl', true);
    $('#detail_map_canvas').gmap('option', 'streetViewControl', true);
    $('#detail_map_canvas').gmap('option', 'mapTypeControlOptions', {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU});



    //Set up monitoring data graph - no data at this stage - this gets populated when #beachDetailsPage is loaded with station code
    options = {
        chart: {
            renderTo: 'monitoring_data_graph',
                backgroundColor: 'rgba(0,0,0,0)',
                defaultSeriesType: 'scatter',
                marginRight: 0,
                marginLeft:65,
                marginTop: 20
            },
            credits: {
                enabled: false
            },
            title: {
                text: null
            },
            colors:['#333333'],
            xAxis: {
                endOnTick: true,
                showLastLabel: false,
                title: {
                    text: 'Date',
                    offset: 30
                },
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%e %b \'%y',
                    week: '%e %b \'%y',
                    month: '%e %b \'%y',
                    year: '%e %b \'%y',
                },
                labels: {
                    rotation: 0,
                    y: 20
                },
                tickWidth: 0
            },
            yAxis: {
                type: 'logarithmic',
                showFirstLabel: false,
                tickPositioner: function(min, max) {
                  var ticks = [1, 10, 100, 1000, 10000],
                      i = ticks.length;

                  while (i--)
                      ticks[i] = this.val2lin(ticks[i]);

                  return ticks;
                },
                labels: {
                    formatter: function(){
                      return this.value < 10 ? 1 : this.value;
                    }
                },
                gridLineWidth: 0,
                lineWidth: 1,
                title: {
                    text: 'Bacteria per 100 mL',
                    margin: 25
                },
                plotBands: [{
                    color: '#96ca2d',
                    from: advisory_limits['Low'].min_limit,
                    to: advisory_limits['Low'].max_limit},
                    {color: '#F9FA4A',
                    from: advisory_limits['Medium'].min_limit,
                    to: advisory_limits['Medium'].max_limit},
                    {color: '#DB1A0F',
                    from: advisory_limits['High'].min_limit,
                    to: 10000}
                    ]

              /*
                plotBands: [{
                    color: '#96ca2d',
                    from: 0,
                    to: 50},
                    {color: '#F9FA4A',
                    from: 50,
                    to: 104},
                    {color: '#DB1A0F',
                    from: 104,
                    to: 10000}
                    ]
               */
            },
            tooltip: {
                formatter: function() {
                    return '<strong>Date:</strong> ' + Highcharts.dateFormat('%e %B %Y', this.x) + '<br /><strong>Bacteria level:</strong> ' + Math.round(this.y);
                }
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'Station',
                data: []
        }]

    };

  });


  $('#beachDetailsPage').bind('pagebeforeshow', function(event) {

    //To set the currently active tab to the data tab, otherwise map will open first if it was left open from a previous beach details view
    $('#details_map_tab_link').removeClass("ui-btn-active");
    $('#details_data_tab_link').addClass("ui-btn-active");
    $('#data_panel').addClass('ui-tabs-content-active');
    $('#map_panel').removeClass('ui-tabs-content-active');

    $('#beachDetails li').remove();


    //Populate details at top of graph
    var station = stations_records.StationData($.mobile.pageData.id)
    var sample_date = station.SampleDate();
    //var sampling_date = new Date(parseDate(currentEtcoc[$.mobile.pageData.id].date));
    var sampling_date = new Date(parseDate(sample_date));

    var forecast = 'None';
    /*
    if(typeof predictionData[$.mobile.pageData.id] === "undefined" || predictionData[$.mobile.pageData.id].ensemble == "NO TEST"){
      var forecast = 'None';
    }
    else{
    */
    if(station.EnsembleResult() !== undefined && station.EnsembleResult() != 'NO TEST')
    {
      //var forecast = predictionData[$.mobile.pageData.id].ensemble;
      forecast = station.EnsembleResult();
    }

    //var shortName = $.trim(currentEtcoc[$.mobile.pageData.id].desc).replace(/\(.*?\)/g, '').replace(/^(.{23}[^\s]*).*/, "$1");
    var shortName = $.trim(station.Description()).replace(/\(.*?\)/g, '').replace(/^(.{23}[^\s]*).*/, "$1");
    $('#beachName').text(shortName);

    var data = 'None';
    /*if(typeof currentEtcoc[$.mobile.pageData.id].value === "undefined"){
      data = 'None';
    }*/
    if(station.SampleValue() !== undefined){
      //data = currentEtcoc[$.mobile.pageData.id].value;
      data = station.SampleValue();
    }

    //$('#beachDetails').append('<li data-theme="d" style="padding:0"><span class="'+forecast.toLowerCase().replace(' ','')+' details-rating">' + capitalize(forecast) + '</span><span class="' +calcAdvisoryRating(currentEtcoc[$.mobile.pageData.id])+ ' details-rating">'+currentEtcoc[$.mobile.pageData.id].advisory+'</span><span class="'+calcDataRating(data, currentEtcoc[$.mobile.pageData.id])+' details-rating">'+data+'&nbsp;&nbsp;</em></span></span></a></li>');
    $('#beachDetails').append('<li data-theme="d" style="padding:0"><span class="'+forecast.toLowerCase().replace(' ','')+' details-rating">' + capitalize(forecast) + '</span><span class="' +calcAdvisoryRating(station)+ ' details-rating">'+station.SampleStationMessage()+'</span><span class="'+calcDataRating(data, station)+' details-rating">'+data+'&nbsp;&nbsp;</em></span></span></a></li>');

  });


  //graph generation needs to be on pageshow, else x-axis labels are cut off
  $('#beachDetailsPage').bind('pageshow', function(event) {
    var station = stations_records.StationData($.mobile.pageData.id);

    var graphHeight = getScreenSize('height') - document.getElementById('detailsheader').offsetHeight - document.getElementById('beachDetailsContainer').offsetHeight;
    //If phone size screen gets rotated to landscape, graph height is not enough for effective viewing of graph so set it to getScreenSize('height') - user can then scroll down to see the rest of the graph which is fullscreen
    if(graphHeight < 200){
      graphHeight = getScreenSize('height')-30;
    }

    //if(typeof predictionData[$.mobile.pageData.id] === "undefined" || predictionData[$.mobile.pageData.id].ensemble == "NO TEST"){
    var forecast = 'None';
    if(station.EnsembleResult() == "NO TEST" || station.EnsembleResult() === undefined){
      forecast = 'None';
    }
    else{
      //forecast = predictionData[$.mobile.pageData.id].ensemble;
      forecast = station.EnsembleResult();
    }

    $('#monitoring_data_graph').css( "height", graphHeight );

    var detailsMapHeight = getScreenSize('height') - document.getElementById('detailsheader').offsetHeight + 4;
    $('#detail_map_canvas').css( "height", detailsMapHeight );


    //Create the beach details map
    $('#detail_map_canvas').gmap('clear', 'markers'); //clear the marker from the last beach details view

    var location = station.Location();
    $('#detail_map_canvas').gmap('addMarker', {
      //'position': new google.maps.LatLng(currentEtcoc[$.mobile.pageData.id].lat,currentEtcoc[$.mobile.pageData.id].lng),
      'position': new google.maps.LatLng(location[1],location[0]),
      'icon': 'static/images/'+forecast.toLowerCase()+'_marker.png',
      'bounds': false

    });


    if(typeof userLat !== 'undefined'){
      var clientPosition = new google.maps.LatLng(userLat, userLng);
      $('#detail_map_canvas').gmap('addMarker', {'position': clientPosition, 'icon': 'static/images/blue_dot_circle.png', 'bounds': false});
    }
    else{
      initializeGeoDetail();
    }

    //$('#detail_map_canvas').gmap('option', 'center', new google.maps.LatLng(currentEtcoc[$.mobile.pageData.id].lat,currentEtcoc[$.mobile.pageData.id].lng));
    $('#detail_map_canvas').gmap('option', 'center', new google.maps.LatLng(location[1],location[0]));
    $('#detail_map_canvas').gmap('option', 'zoom', 19);

    $('#detail_map_canvas').gmap('refreshCenter');



    // Populate the graph - framework for graph is set up above
    monitoringChart = new Highcharts.Chart(options);

    var series = {
    data: []
    };

    //Using $.ajax and async: false, rather than $.getJSON to ensure that testData is populated before page tries to use it.
    var get_data = {'station': $.mobile.pageData.id,
                    'startdate': ISODateString(date_by_subtracting_days(current_date, 365))
                  };
    $.ajax({
      type: "GET",
      cache : false,
      async: false,
      crossDomain: false,
      timeout: 5000,
      url: "/station_data/" + site + '/' + $.mobile.pageData.id,
      data: get_data,
      dataType: "json",
      success: function(testData) {
        $.each(testData.contents.properties.test.beachadvisories, function(i,j){
          if(parseInt(j.value,10)===0 || j.value=='<10'){
            j.value=1;
          }
          series.data.push([parseDate(j.date),parseInt(j.value,10)]);
        });

        monitoringChart.series[0].setData(series.data);
        monitoringChart.xAxis[0].setExtremes(Date.parse(date_by_subtracting_days(current_date, 365)),Date.parse(current_date));
      }
    });



    $('body').removeClass('ui-loading');

  });

}
