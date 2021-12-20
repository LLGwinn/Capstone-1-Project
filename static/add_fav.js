favBtn = $('#fav-btn');
icon = favBtn.find('i');

favBtn.click(addFav);

async function addFav() {

    const id = $(this).data('id');

    if (icon.hasClass('fas')) {
        icon.removeClass('fas');
        icon.removeClass('text-danger')
        icon.addClass('far');
        icon.addClass('text-secondary')
    }
    else {
        icon.removeClass('far');
        icon.removeClass('text-secondary')
        icon.addClass('fas');
        icon.addClass('text-danger')
    }

}
