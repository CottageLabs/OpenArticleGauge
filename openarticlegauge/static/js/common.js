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
        
        all_e = $('[id^=journal_urls-]');
        e = all_e.last();
        ne = e.clone()[0];
        ne.value = '';
        items = ne.id.split('-');
        number = parseInt(items.pop());
        number = number + 1;
        new_id = 'journal_urls-' + number;
        ne.id = new_id;
        ne.name = new_id;
        e.after(ne);
        e.after('<br>');        
        
		event.preventDefault(); // prevent form submission
    });
        
    $('.btn.more_licenses').click( function (event) {
        
        all_e = $('[id^=licenses-][id$="container"]');
        e = all_e.last();
        ne = e.clone()[0];
        ne.value = '';
        items = ne.id.split('-');
        number = parseInt(items[1]);
        number = number + 1;
        new_id = 'licenses-' + number + '-container';
        ne.id = new_id;
        ne = $(ne);
        ne.find('[id^=licenses-]').each( function () {
            var ce = $(this);
            ce.attr('value', '');
            console.log(ce);
            console.log(ce.attr('id'));
            items = ce.attr('id').split('-');
            number = parseInt(items[1]);
            number = number + 1;
            new_id = 'licenses-' + number + '-' + items[2];
            ce.attr('id', new_id);
            ce.attr('name', new_id);
            ce.siblings('.resolved_doi').remove();
            

        });
        e.after(ne);
        $('[id^=licenses-][id$="example_doi"]').focusout(resolve_doi);
        
		event.preventDefault(); // prevent form submission
        
           
	});
    
    $('[id^=licenses-][id$="example_doi"]').focusout(resolve_doi);
    
});

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
