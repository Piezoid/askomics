/*jshint esversion: 6 */

import * as Handlebars from 'handlebars'

import { displayModal, hideModal } from './utils/Modal';
import RestServiceJs from './utils/RestManagement';

import * as askomics from './main';


let askomicsInitialization = false;
function startRequestSessionAskomics() {
  if ( askomicsInitialization ) return ;
  // Initialize the graph with the selected start point.
  $("#init").hide();
  $("#queryBuilder").show();
  $("svg").remove();

  askomicsInitialization = true;
}

function startVisualisation() {
    //Following code is automatically executed at start or is triggered by the action of the user
    startRequestSessionAskomics();
    askomics.forceLayoutManager.start();
}


function loadStartPoints() {

  var service = new RestServiceJs("startpoints");
  $("#btn-down").prop("disabled", true);
  $("#showNode").hide();
  $("#deleteNode").hide();

  service.getAll(function(startPointsDict) {
      $("#startpoints").empty();

      $.each(startPointsDict.nodes, function(key, value) {

          $("#startpoints").append($("<option></option>").attr("data-value", JSON.stringify(value)).text(value.label));
      });
      $("#starter").prop("disabled", true);
      $("#startpoints").click(function(){
          if ($("#starter").prop("disabled")) {
              $("#starter").prop("disabled", false);
          }
      });
  });
}

function loadStatistics(modal) {

  if (modal) {
    displayModal('Please Wait', '', 'Close');
  }

  const userAbstraction = askomics.userAbstraction;



  var service = new RestServiceJs("statistics");
  service.getAll(function(stats) {
    $('#content_statistics').empty();
    $('#content_statistics')
    .append($("<p></p>").text("Number of triples  : "+stats.ntriples))
    .append($("<p></p>").text("Number of entities : "+stats.nentities))
    .append($("<p></p>").text("Number of classes : "+stats.nclasses))
    .append($("<div id='deleteButtons'></div>"));

    $("#deleteButtons").append("<p><button id='btn-empty' onclick='emptyDatabase(\"confirm\")' class='btn btn-danger'>Empty database</button></p>");

    let table=$("<table></table>").addClass('table').addClass('table-bordered');
    let th = $("<tr></tr>").addClass("table-bordered").attr("style", "text-align:center;");
    th.append($("<th></th>").text("Class"));
    th.append($("<th></th>").text("Nb"));
    table.append(th);

    $.each(stats['class'], function(key, value) {
      let tr = $("<tr></tr>")
            .append($("<td></td>").text(key))
            .append($("<td></td>").text(value.count));
      table.append(tr);
    });
    $('#content_statistics').append(table);

    var entities = userAbstraction.getEntities() ;

    table=$("<table></table>").addClass('table').addClass('table-bordered');
    th = $("<tr></tr>").addClass("table-bordered").attr("style", "text-align:center;");
    th.append($("<th></th>").text("Class"));
    th.append($("<th></th>").text("Relations"));
    table.append(th);

    for (var ent1 in entities ) {
      let tr = $("<tr></tr>")
            .append($("<td></td>").text(userAbstraction.removePrefix(entities[ent1])));
            let rels = "";
            var t = userAbstraction.getRelationsObjectsAndSubjectsWithURI(entities[ent1]);
            var subjectTarget = t[0];
            for ( var ent2 in subjectTarget) {
              for (var rel of subjectTarget[ent2]) {
                rels += userAbstraction.removePrefix(entities[ent1]) + " ----" + userAbstraction.removePrefix(rel) + "----> " + userAbstraction.removePrefix(ent2) + "</br>";
              }
            }

            tr.append($("<td></td>").html(rels));
      table.append(tr);
    }

    $('#content_statistics').append(table);


    table = $("<table></table>").addClass('table').addClass('table-bordered');
    th = $("<tr></tr>").addClass("table-bordered").attr("style", "text-align:center;");
    th.append($("<th></th>").text("Class"));
    th.append($("<th></th>").text("Attributes"));
    table.append(th);

    for (ent1 in entities ) {
    //$.each(stats['class'], function(key, value) {
      let tr = $("<tr></tr>")
            .append($("<td></td>").text(userAbstraction.removePrefix(entities[ent1])));
            let attrs = "";
            let cats = "";
            var listAtt = userAbstraction.getAttributesEntity(entities[ent1]);
            for (var att of listAtt) {
                attrs += '- '+att.label +' :'+userAbstraction.removePrefix(att.type)+ "</br>";
            }
            tr.append($("<td></td>").html(attrs));
      table.append(tr);
    //});
    }
    if (modal) {
        hideModal();
    }

    $('#content_statistics').append(table);

  });
}

function emptyDatabase(value) {
    if (value == 'confirm') {
        $("#deleteButtons").empty();
        $("#deleteButtons")
        .append('<p>Delete all data ? ')
        .append("<button id='btn-empty' onclick='emptyDatabase(\"yes\")' class='btn btn-danger'>Yes</button> ")
        .append("<button id='btn-empty' onclick='emptyDatabase(\"no\")' class='btn btn-default'>No</button></p>");
        return;
    }

    if (value == 'no') {
        $("#deleteButtons").empty();
        $("#deleteButtons").append("<p><button id='btn-empty' onclick='emptyDatabase(\"confirm\")' class='btn btn-danger'>Clear database</button></p>");
        return;
    }

    if (value == 'yes') {
        displayModal('Please wait ...', '', 'Close');
        var service = new RestServiceJs("empty_database");
            service.getAll(function(empty_db){
              hideModal();
              if ('error' in empty_db ) {
                alert(empty_db.error);
              }
            loadStatistics(false);
        });
    }
}


function downloadTextAsFile(filename, text) {
    // Download text as file
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}


$(function () {
  // TODO: move inside AskomicsMenuFile
    // Startpoints definition
    loadStartPoints();

    // Loading a sparql query file
    $(".uploadBtn").change( function(event) {
      var uploadedFile = event.target.files[0];
      if (uploadedFile) {
          var fr = new FileReader();
          fr.onload = function(e) {
            var contents = e.target.result;
            startRequestSessionAskomics();
            askomics.forceLayoutManager.startWithQuery(contents);
          };
          fr.readAsText(uploadedFile);
      }
    });

    // Get the overview of files to integrate
    $("#integration").click(function() {
        var service = new RestServiceJs("up/");
        service.getAll(function(formHtmlforUploadFiles) {
          $('div#content_integration').html(formHtmlforUploadFiles.html);
          // Dynamically load integration components
          require.ensure(['./integration'], require =>
            require<any>('./integration').startUploadForm());
          }, 'integration');
    });

    // Visual effect on active tab (Ask! / Integrate / Credits)
    $('.nav li').click(function(e) {
        $('.nav li.active').removeClass('active');
        var $this = $(this);
        if (!$this.hasClass('active')) {
            $this.addClass('active');
        }
        $('.container').hide();
        $('.container#navbar_content').show();
        $('.container#content_' + $this.attr('id')).show();
        e.preventDefault();
    });

    // A helper for handlebars
    Handlebars.registerHelper('nl2br', function(text) {
        var nl2br = (text + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + '<br>' + '$2');
        return new Handlebars.SafeString(nl2br);
    });
});

window.askomics = Object.assign({startVisualisation, loadStartPoints, loadStatistics}, askomics);
