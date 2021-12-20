$('.delete-fav').click(deleteFav);

async function deleteFav() {
    const id = $(this).closest('div.row').data('id');

    await axios.delete(`/users/favs/delete/${id}`);

    $(this).closest('div.row').remove();
}