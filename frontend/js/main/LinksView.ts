/*jshint esversion: 6 */
import * as nodeView from './NodeView';
import * as linksView from './LinksView';
import * as forceLayoutManager from './ForceLayoutManager';
/*
  Manage Information Link View With a current selected link
*/
  var prefix = "rightview_";
  var arrowCode = "&#8594;";

export function remove (link) {
    $("#"+prefix+"Link-"+link.id).remove();
  };

function showTitle (link) {

    nodeView.clean();
    $("#objectName").text(link.label);

  };

export function show (link) {
    showTitle(link);
    $("#"+prefix+"Link-"+link.id).show();
  };

export function hide (link) {
    $("#"+prefix+"Link-"+link.id).hide();
  };

export function hideAll () {
    $("div[id*='"+ prefix +"']" ).hide();
  };

function changeType(link, type) {

    // remove link
    var id = link.id;
    $('#'+id).remove(); // link
    $('#label-'+id).remove(); // link label
    $('#marker-'+id).remove(); // arrow

    // change link type and label
    link.type = type;
    var labels = {'included':'included in', 'excluded':'exluded of', 'overlap':'overlap with', 'near': 'near'};
    link.label = labels[type];

    // If overlap, don't show reverse query (it is the same)
    if (type == 'overlap') {
      $('#change_dir-div-'+id).hide();
    }else{
      if ($('#change_dir-div-'+id).is(":hidden")) {
        $('#change_dir-div-'+id).show();
      }
    }

    // reload graph (it will recreate the link)
    forceLayoutManager.update();
    //select the link
    forceLayoutManager.selectLink(link);
  };

function reverseDir(link) {

    // remove rightview
    remove(link);

    // remove link
    var id = link.id;
    var linkid = $('#'+id).attr("idlink");

    $('#'+id).remove(); // link
    $('#label-'+id).remove(); // link label
    $('#marker-'+id).remove(); // arrow

    // swap target and source
    var buf = link.source ;
    link.source = link.target;
    link.target = buf;

    // new rightview for the reverse link
    create(link);

    // reload graph (it will recreate the link)
    forceLayoutManager.update();
    //select the link
    forceLayoutManager.selectLink(link);
  };

export function changeStrict(link, strict) {
    link.strict = strict;
  };

export function changeSameTax(link, same_tax) {
    link.sameTax = same_tax;
  };

export function changeSameRef(link, same_ref) {
    link.sameRef = same_ref;
  };

export function create (link) {
    if(link.positionable){
      createPosistionableView(link);
    }else{
      createStandardView(link);
    }
  };

function createStandardView (link) {

    var id_link = link.id;

    var elemUri = link.uri,
         nameDiv = prefix+"Link-"+id_link ;

    showTitle(link);
    var details = $("<div></div>").attr("id",nameDiv)
                                  .addClass('div-details')
                                  .append("No filter available");

    $("#viewDetails").append(details);
  };

function createPosistionableView (link) {

    var id_link = link.id;

    var elemUri = link.uri,
         nameDiv = prefix+"Link-"+id_link ;

    showTitle(link);

    var details = $("<div></div>").attr("id",nameDiv).addClass('div-details');
    //console.log(JSON.stringify(link.target));

    var reverseArrow = $('<div></div>').attr('id', 'change_dir-div-'+id_link).append($('<span><span>').attr('class', 'glyphicon glyphicon-resize-horizontal')
                                                                .attr('aria-hidden', 'true')
                                                                .attr('id', 'change_dir-'+id_link))
                                       .append('Reverse direction');

    var select = $('<select></select>').attr('id', 'type-'+id_link);

    // Uncomment near when near query is OK
    var types = {'included': 'included in', 'excluded': 'excluded of', 'overlap': 'overlap with'/*, 'near': 'near'*/};

    for (var key in types) {
      if(link.type == key) {
          select.append($('<option></option>').attr("value", key).attr("selected", "selected").append(types[key]));
      }else{
          select.append($('<option></option>').attr("value", key).append(types[key]));
      }
    }

    var relation = $("<div></div>").append(nodeView.formatLabelEntity(link.source))
                               .append(select)
                               .append(nodeView.formatLabelEntity(link.target));

    var checkbox_sameref;
    var checkbox_sametax;

    if (link.sameRef) {
      checkbox_sameref = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'ref-'+id_link).attr('checked', 'checked')).append('Reference');
    }else{
      checkbox_sameref = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'ref-'+id_link)).append('Reference');
    }

    if (link.sameTax) {
      checkbox_sametax = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'tax-'+id_link).attr('checked', 'checked')).append('Taxon');
    }else{
      checkbox_sametax = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'tax-'+id_link)).append('Taxon');
    }


    var onTheSame = $('<div></div>').append('On the same:')
                                    .append($('<br>'))
                                    .append(checkbox_sameref)
                                    .append($('<br>'))
                                    .append(checkbox_sametax);

    var strict;

    if (link.strict) {
      strict = $('<div></div>').append($('<label></label>').append($('<input>').attr('type', 'checkbox').attr('checked', 'checked').attr('id', 'strict-'+id_link).attr('value', 'strict')).append('Strict'));
    }else{
      strict = $('<div></div>').append($('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'strict-'+id_link).attr('value', 'strict')).append('Strict'));
    }

    details//.append(reverseArrow)
           .append(relation).append(reverseArrow)
           .append($('<hr>'))
           .append(onTheSame)
           .append($('<hr>'))
           .append(strict);

    select.change(function() {
      let value = select.val();
      changeType(link, value);
    });

    checkbox_sameref.change(function() {
      if ($('#ref-'+id_link).is(':checked')) {
        changeSameRef(link, true);
      }else{
        changeSameRef(link, false);
      }
    });

    checkbox_sametax.change(function() {
      if($('#tax-'+id_link).is(':checked')) {
        changeSameTax(link, true);
      }else{
        changeSameTax(link, false);
      }
    });

    strict.change(function() {
      if($('#strict-'+id_link).is(':checked')) {
        changeStrict(link, true);
      }else{
        changeStrict(link, false);
      }
    });

    reverseArrow.click(function() {
      console.log('---> ReverseDir');
      reverseDir(link);
    });

    $("#viewDetails").append(details);
  };

  // take a string and return an entity with a sub index
export function selectListLinksUser(links,node) {
    /* fix the first link associted with the new instanciate node TODO: propose an interface to select the link */
    for (var il in links) {
      var l = links[il];
      console.log("===>"+JSON.stringify(l));
      if ( l.suggested && (l.source.id == node.id || l.target.id == node.id) ) {
        return [links[il]];
      }
    }
  };
