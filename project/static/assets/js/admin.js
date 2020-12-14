$(document).ready(function() {

    if(notAdmin){
        Swal.fire({
            icon: 'error',
            title: 'Acceso denegado.',
            text: 'Parece que no posees permisos para acceder a esta pantalla',
          }).then((result) => {
            location.href = "/inicio"
          })
    }

    $('#dataTable').DataTable({
        "language": {
            "lengthMenu": "Mostrando _MENU_ registros por página",
            "zeroRecords": "No se encuentran registros",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "infoEmpty": "No se encuentran registros",
            "infoFiltered": "(Filtrado de _MAX_ registros totales)",
            "lengthMenu":     "Mostrar _MENU_ registros",
            "search" : "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Última",
                "next":       "Siguiente",
                "previous":   "Anterior"
            },
        }
    } );
  });

function deleteUser(id, nombre) {
    Swal.fire({
        title: '¿Seguro desea eliminar el usuario "'+ nombre+'"?',
        text: "No se podrá recuperar una vez eliminado!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si borrar!',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          location.href = "eliminar/"+id;
        }
      })
}