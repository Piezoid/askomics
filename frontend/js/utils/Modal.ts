
export function displayModal(title, message, button) {
    $('#modalTitle').text(title);
    if (message == '') {
      $('.modal-body').hide();
      $('.modal-sm').css('width', '300px');
    }else{
      $('.modal-sm').css('width', '700px');
      $('.modal-body').show();
      $('#modalMessage').text(message);
    }
    $('#modalButton').text(button);
    $('#modal').modal('show');
}

export function hideModal(){
    $('#modal').modal('hide');
}
