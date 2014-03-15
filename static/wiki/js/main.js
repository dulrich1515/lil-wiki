function Toggle(id)
{
  e = document.getElementById(id).style;
  e.display = ( e.display != 'block' ) ? 'block' : 'none';
}

function buttonToggle(where, showLabel, hideLabel, disp) {
    if(typeof(disp)==='undefined') disp = 'block';
    where.value = (where.value == showLabel) ? hideLabel : showLabel;
    var e = document.getElementById(where.attributes.rel.value);
    e.style.display = (e.style.display == disp) ? 'none' : disp;
}

function FindFocus()
{
  bFound = false;
  for ( f = 0; f < document.forms.length; f++ )
  {
    for ( i = 0; i < document.forms[f].length; i++ )
    {
      if ( document.forms[f][i].type != "hidden" && document.forms[f][i].disabled != true )
      {
        document.forms[f][i].focus();
        bFound = true;
      }
      if ( bFound == true ) break;
    }
    if ( bFound == true ) break;
  }
}



$(document).keydown(function(e) {
    var keycode = e.which || e.keyCode;
    var key = String.fromCharCode(keycode).toLowerCase()

    if ( keycode == 27 ) // escape
    {
        e.preventDefault();
        var elem = document.getElementById("control_list").style;
        elem.display = ( elem.display != 'none' ) ? 'none' : 'block';
    }
});


$(document).ready(function() {
    $('.toggler').val( function( index, val ) {
        return val + ' ▸'; // ◂
    });
    $('.toggler').click(function () {
        $(this).parent().next('.togglee').toggle();
        var v1 = $(this).val().slice(0, -1);
        var v2 = $(this).val().slice(-1);
        v2 = ( v2 == '▸' ) ? '◂' : '▸'
        $(this).val(v1 + v2);
    });
});


