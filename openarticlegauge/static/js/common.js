jQuery(document).ready(function() {
// All of these will run for ANY page.
/* There is very little possibility that any pages will break due to the class
 * names used (specific enough). Where the selectors are more general, this is
 * intentional - the point is to enable quick and easy re-use of code. If a
 * "Tags" field is needed then it will likely need an "add more" [tags] button
 * no matter which page it is on. Copying the relevant HTML is all which will
 * be necessary since the code below runs for all pages.
 */ 

	// "add more" button 
	$('.btn.journal_link').click( function (event) {
        
        // var all_e = $('[id^=journal_urls-]').parent().parent();
        var all_e = $('.journal_urls-container');
        var e = all_e.last();
        var ne = $(e.clone()[0]);
        var input_ne = $(ne.find('[id^=journal_urls-]')[0]);
        var input_wrapper_div = $(ne.children('div.controls')[0]);
        input_wrapper_div.children().slice(1).remove();
        input_ne.addClass('span10');
        input_ne.attr('value', '');
        var items = input_ne.attr('id').split('-');
        var number = parseInt(items.pop());
        number = number + 1;
        var new_id = 'journal_urls-' + number;
        input_ne.attr('id', new_id);
        input_ne.attr('name', new_id);

        var remove_e = '<a class="btn btn-danger remove-button" id="remove-' + new_id + '" href="#remove-' + new_id + '">&times;</a>';
        input_ne.after(remove_e);
        add_remove_btn_handler();
        e.after(ne);
               
		event.preventDefault(); // prevent form submission
    });
        
    $('.btn.more_licenses').click( function (event) {
        
        var all_e = $('[id^=licenses-][id$="container"]');
        var e = all_e.last();
        var ne = $(e.clone()[0]);
        ne.children().slice(1).remove();
        var items = ne.attr('id').split('-');
        var number = parseInt(items[1]);
        number = number + 1;
        var new_id = 'licenses-' + number + '-container';
        ne.attr('id', new_id);
        ne.find('[id^=licenses-]').each( function () {
            var ce = $(this);
            ce.attr('value', '');
            var items = ce.attr('id').split('-');
            var number = parseInt(items[1]);
            number = number + 1;
            var new_id = 'licenses-' + number + '-' + items[2];
            ce.attr('id', new_id);
            ce.attr('name', new_id);
            ce.siblings('.resolved_doi').remove();
        });
        ne.children('.inner-container').removeClass('span12').addClass('span11');

        e.after(ne);

        var remove_e = '<a class="btn btn-danger remove-button license-remove-button" id="remove-' + new_id + '" href="#remove-' + new_id + '">&times;</a>';
        ne.append(remove_e);
        add_remove_btn_handler();

        $('[id^=licenses-][id$="example_doi"]').focusout(resolve_doi);
        
		event.preventDefault(); // prevent form submission
	});
    
    add_remove_btn_handler();
    $('[id^=licenses-][id$="example_doi"]').focusout(resolve_doi);
    
});

function add_remove_btn_handler() {
    $('.remove-button').click ( function (event) {
        var e = $(this);
        var id = e.attr('id').slice('remove-'.length);
        id = id.slice(0, id.lastIndexOf('-'));
        id = id + '-container';
        $('#' + id).remove(); // attempt to remove the specific id first, the container might have it

        // then try by class of the container
        one_of_these_needs_to_be_removed = $('.' + id);
        for (var i = 0; i < one_of_these_needs_to_be_removed.length; i++) {
            current = $(one_of_these_needs_to_be_removed[i]);
            console.log(current.find('#' + e.attr('id')).length);
            if (current.find('#' + e.attr('id')).length !== 0) {
                current.remove();
            }
        }
        event.preventDefault();
    });
}

function getOuterHTML(selector) {
    /* There is no easy way to get the outerHTML of an element in jQuery.
     * This is needed since we want to duplicate the useful link <input>.
     * The code below does .clone().wrap('<p>').parent().html()
     *
     * The way it works is that it takes the first element with a certain
     * class, makes a clone of it in RAM, wraps with a P tag, gets the parent 
     * of it (meaning the P tag), and then gets the innerHTML property of that.
     * So we end up copying the element we just selected, which is our goal.
     
     * The clone() means we're not actually disturbing the DOM. Without it
     * all elements with a certain class will be wrapped in a P tag which is
     * undesirable.
     */
	return $(selector).clone().wrap('<p>').parent().html();
}

function resolve_doi() {
    var elem = $(this);
    var doi = elem.val();
           
    if (doi) {
        $.ajax({
            type: "GET",
            async: true,
            url: '/resolve_doi/' + doi,
            success: function(data, textStatus, jqXHR) { 
                elem.siblings('.resolved_doi').remove();
                elem.after(
                    '<p class="resolved_doi"><a target="_blank" href="'+ data + '">'+ data +'</a></p>'
                    ); 
            },
            error: function(jqXHR, textStatus, errorThrown ) { elem.after(
            '<p class="resolved_doi">Could not contact OAG. '+ errorThrown +'</p>'
            ); }
          
        
        });
    }
    
      
}
