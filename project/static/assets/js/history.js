$(document).ready(function () {

  $('#dataTable').DataTable({
    "language": {
      "lengthMenu": "Mostrando _MENU_ registros por página",
      "zeroRecords": "No se encuentran registros",
      "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
      "infoEmpty": "No se encuentran registros",
      "infoFiltered": "(Filtrado de _MAX_ registros totales)",
      "lengthMenu": "Mostrar _MENU_ registros",
      "search": "Buscar:",
      "paginate": {
        "first": "Primera",
        "last": "Última",
        "next": "Siguiente",
        "previous": "Anterior"
      },
    }
  });
});

function deleteCalculo(id) {
  Swal.fire({
    title: '¿Seguro desea eliminar el usuario "' + nombre + '"?',
    text: "No se podrá recuperar una vez eliminado!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Si borrar!',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      location.href = "eliminar/" + id;
    }
  })
}