#Examples and location of licensing information for specific publishers

##Outline

The purpose of this document is to identify the source of licensing information in the html pages provided by different scholarly publishers and to provide a test set of documents associated with authoritative statements of the license status.

The HTML documents are the result of dereferencing specified DOIs. They therefore vary as to whether they contain abstracts or full text papers. For each publisher there are multiple examples provided that have different license status.

##BioMedCentral

The vast majority of papers published by BMC are made available under a CC BY license. There are some exceptions for commentaries and reviews that are available to subscribers and (need to check whether any complexities in BMC papers with OGL, PD, or WHO).

Journals that contain non-open access content can be found via the list of journals where they are annotated: http://www.biomedcentral.com/journals

###Examples
####An open access article

DOI:10.1186/1471-2164-13-425

Dereferenced URL: http://www.biomedcentral.com/1471-2164/13/425

Status: Open Access

License: CC BY v2.0

The licensing information is contained in a number of places in the html document. The most reliable source is found as a meta tag:

	<meta name="dc.rights" content="http://creativecommons.org/licenses/by/2.0/" />and in the human readable text at the bottom of <section class="cit"> as follows:

	<section class="cit">
	<div class="collapsible-content">	[…other citation content…]
	<p>
	This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.
	</p>
	</div>
	</section>

####A non-open access article

DOI: 10.1186/bcr3351

Dereferenced URL: http://breast-cancer-research.com/content/14/6/327

Status: Not Accessible, Not Open Access, Accessible with subscription

License: Not available
The license information elements that are visible in the Open Access article are not present at the dereferenced URL for the non-open access article.

##PLOS


The majority of PLOS articles are made available under a Creative Commons Attribution license with no version specified in the human readable text. Some articles, particularly older ones, have non-standard license text. There are also at least three variants licenses deployed, ccZero for work exclusive authored by US Government Employess, the UK Open Government License, and a generic WHO License which specifies non-commercial terms.

###Examples
####A standard CC BY article

DOI: 10.1371/journal.pbio.1001461

Dereferenced URL: http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461

Status: Open Access

License: CC BY, version not specified

The license is found a <div class="articleinfo"> as a separate paragraph as follows:

	<div class="articleinfo">
	[…]
	<p><strong>Copyright:</strong>
	 © 2012 Kalyuga et al. This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.
	</p>
	[…]
	</div>

####A legacy PLOS OA license article

DOI:10.1371/journal.pbio.0000021
Dereferenced URL: http://www.plosbiology.org/article/info:doi/10.1371/journal.pbio.0000021

Status: Open Access

License: Not specified but rights consistent with CC BY

The license is found in the same div element as above:

	<div class="articleinfo">
	[…]
	<p><strong>Copyright:</strong>
	 © 2003 Braendle et al. This is an open-access article distributed under the terms of the Public Library of Science Open-Access License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.
	</p>
	[…]
	</div>

####A WHO licensed article

DOI: 10.1371/journal.pmed.1001062
Dereferenced URL: http://www.plosmedicine.org/article/info%3Adoi%2F10.1371%2Fjournal.pmed.1001062

Status: Accessible

License: Not specified, no advertisement, non-commercial terms.

The licensing terms are found in the same div element as above:

	<div class="articleinfo">
	[…]
	<p>
	<strong>Copyright:</strong> © 2011 World Health Organization; licensee Public Library of Science (PLoS). This is an Open Access article in the spirit of the Public Library of Science (PLoS) principles for Open Access http://www.plos.org/oa/, without any waiver of WHO's privileges and immunities under international law, convention, or agreement. This article should not be reproduced for use in association with the promotion of commercial products, services, or any legal entity. There should be no suggestion that WHO endorses any specific organization or products. The use of the WHO logo is not permitted. This notice should be preserved along with the article's original URL.
	</p>
	[…]
	</div>

####Article under the UK OGL

DOI: 10.1371/journal.pone.0035089

Dereferenced URL: http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089

Status: Open Access

License: Open Government Licence (UK)

The licensing terms are found in the same div element as above:

	<div class="articleinfo">
	[…]
	<p>
	<strong>Copyright:</strong> © 2012 Crown Copyright. This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.
	[…]
	</p>
	</div>

####A CC-Zero (Public Domain Dedication) article

DOI: 10.1371/journal.pone.0037743

Dereferenced URL: http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0037743

Status: Open Access

License: CC Zero (Public Domain Dedication), version not specified (only v.1.0 published at time of writing)

The license is found a <div class="articleinfo"> as a separate paragraph as follows:

	<div class="articleinfo">
	[…]
	<strong>Published:</strong> May 30, 2012</p>
	<p>This is an open-access article, free of all copyright, and may be freely reproduced, distributed, transmitted, modified, built upon, or otherwise used by anyone for any lawful purpose. The work is made available under the Creative Commons CC0 public domain dedication.</p>
	<p><strong>Funding: </strong>
	[…]
	</div>

##Below here still needs work!	

##OUP

Oxford University Press runs a range of journals with Open Access content of one sort of another. They generally have a mix of CC BY-NC and CC BY licensing. Journals tend to be wholly Open Access or not rather than mixed but there is some hybrid content. OUP seem to be quite consistent about their copyright statements which is helpful. In the rendered html the copyright statements link terms pages but the copyright statements for CC licensed articles all seem to include a link to a specific CC license.

###Bioinformatics

Bioinformatics has both OA and non-OA content

####All rights reserved content

DOI: 10.1093/bioinformatics/bts552

Dereferenced URL: http://bioinformatics.oxfordjournals.org/content/28/22/2891

Status: Not Open Access

License: © The Author, All rights reserved 

The licensing terms are found between the main article div and the right column div in an unordered list element:

	<ul class="copyright-statement">
        <li class="fn" id="copyright-statement-1">© The Author 2012. Published by Oxford University Press. All rights reserved. For Permissions, please e-mail: journals.permissions@oup.com</li>
        </ul>
	<span class="highwire-journal-article-marker-end"></span></div><span id="related-urls"></span></div>

####OA content with a CC BY license

DOI: 10.1093/bioinformatics/bts553

Dereferenced URL: http://bioinformatics.oxfordjournals.org/content/28/22/2898

Status: Open Access

License: CC BY v3.0

	<ul class="copyright-statement">
        <li class="fn" id="copyright-statement-1">© The Author 2012. Published by Oxford University Press.</li>
        </ul>
        <div class="license" id="license-1">
        <p id="p-2">This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/), which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.
        </p>
        </div>
	<span class="highwire-journal-article-marker-end"></span></div><span id="related-urls"></span></div>


###Nucleic Acids Research

####A CC BY-NC article

DOI: 10.1093/nar/gks793

Dereferenced URL: http://nar.oxfordjournals.org/content/40/21/10832

Status: Accessible, non-commercial restrictions

License: CC BY-NC 3.0

Similar to Bioinformatics the Copyright statement is found in its own div:

	<ul class="copyright-statement">
        <li class="fn" id="copyright-statement-1">© The Author(s) 2012. Published by Oxford University Press.</li>
        </ul>
        <div class="license" id="license-1">
        <p id="p-1">This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.
        </p>
        </div>
	</div><span class="highwire-journal-article-marker-end"></span></div>

####A CC BY article

DOI: 10.1093/nar/gks884

Dereferenced URL: http://nar.oxfordjournals.org/content/40/21/10668

Status: Open Access

License: CC BY 3.0

	<ul class="copyright-statement">
        <li class="fn" id="copyright-statement-1">© The Author(s) 2012. Published by Oxford University Press.</li>
        </ul>
        <div class="license" id="license-1">
        <p id="p-1">This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/), which permits unrestricted, distribution, and reproduction in any medium, provided the original work is properly cited.
        </p>
        </div>

##eLife

eLife is a pure OA publisher where all content should be under a CC BY license but as with BMC and PLOS there are likely to be some exceptions in the future. 

Waiting on info from Ian Mulvany but this seems the obvious source:

DOI: 10.7554/eLife.00160
Dereferenced URL: http://elife.elifesciences.org/content/2/e00160

Status: Open Access

License: CC BY 3.0

Source: 
	<div class="elife-article-indicators">
		<a href="http://www.elifesciences.org/the-journal/open-access">
			<img src="http://dex3165296d6d.cloudfront.net/sites/default/modules/elife/elife_article/images/oa.png" alt="Open access" title="Open access" />
		</a>
		<a href="http://creativecommons.org/licenses/by/3.0/">
			<img src="http://dex3165296d6d.cloudfront.net/sites/default/modules/elife/elife_article/images/cc.png" alt="Copyright info" title="Copyright info" />
		</a>
	</div>

##Cell Reports

Cell Reports is largely Open Access but with a small range of licenses. The DOI dereferences to the Science Direct page rather than to the journal itself. This is a problem because the SD page doesn't have the correct license information.

####Article with CC BY-NC-ND license

DOI: 10.1016/j.celrep.2012.11.027

Dereferenced URL: http://www.sciencedirect.com/science/article/pii/S2211124712004263

Canonical Journal URL: http://www.cell.com/cell-reports/fulltext/S2211-1247(12)00426-3

Status: Publicly Accessible

License: CC BY-NC-ND (no version given)

I can't figure out where the hell the licensing information is in the page source, even for the canonical journal URL where I can find it via the Related Info and then Licensing Info tabs. In the source the tabs appear to call the page content via javascript in a particularly ugly way. I think this might be one to give up on in the first instance.

####Article with a CC BY license

DOI: 10.1016/j.celrep.2012.11.028

Dereferenced URL: http://www.sciencedirect.com/science/article/pii/S2211124712004305

Canonical Journal URL: http://www.cell.com/cell-reports/fulltext/S2211-1247(12)00430-5

Status: Open Access

License: CC BY (no version)

Similar to above. Licensing on the SD version is wrong (or at least misleading) and the tabs that lead to the licensing information on the journal page are obfuscated in a way I don't understand.

##Scientific Reports

Scientific Reports has three different license types. CC BY, CC BY-NC, and CC BY-NC-ND

####CC BY-NC-ND example

DOI: 10.1038/srep01041

Dereferenced URL: http://www.nature.com/srep/2013/130109/srep01041/full/srep01041.html

Status: Publicly Accessible, NC-ND restrictions

License: CC BY-NC-ND 3.0 Unported

The licensing information is provided in the article footer:

	<footer>
	<div class="article-footer">
		<p class="license">
			<a href="http://creativecommons.org/licenses/by-nc-nd/3.0/" class="cc-license by-nc-nd" rel="license">
			<img src="/view/images/icon_by_nc_nd.png"/></a>
			This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of this license, visit  
			<a href="http://creativecommons.org/licenses/by-nc-nd/3.0/">http://creativecommons.org/licenses/by-nc-nd/3.0/</a>
		</p>
						
	</div>
	</footer>

####CC BY Example

DOI: 10.1038/srep01011

Dereferenced URL: http://www.nature.com/srep/2012/121220/srep01011/full/srep01011.html

Status: Open Access

License: CC BY 3.0 Unported

	<footer>
	<div class="article-footer">
		<p class="license">
			<a href="http://creativecommons.org/licenses/by/3.0/" class="cc-license by" rel="license">
			<img src="/view/images/icon_by.png"/></a>
			This work is licensed under a Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>
		</p>
	</div>
	</footer>

##Royal Society of Chemistry

The RSC currently provides little or no useful permissions information.

####"RSC Open Science Free Article" Example

DOI: 10.1039/C2CC35799B

Dereferenced URL: http://pubs.rsc.org/en/Content/ArticleLanding/2012/CC/c2cc35799b

Status: Publicly Accessible

License: None given

	<div class="peptide_wrap_s10_right_inner">
        	<div style="border-bottom:1px solid #D6D6D6; padding:5px 0px 5px 10px;color:#014682">RSC Open Science free article </div>   
		<div id="DownloadOption">
			<img id="imgdownload" style="margin-left: 60px;" title="Please wait while Download options loads"
                         alt="Please wait while Download options loads" src="http://sod-a.rsc-cdn.org/pubs.rsc.org/content/NewImages/Ajax-GA-Loader.gif" />
                </div>
	[…]
	</div>

####Non accessible article

DOI: 10.1039/C2CC36189B

Dereferenced URL: http://pubs.rsc.org/en/Content/ArticleLanding/2012/CC/c2cc36189b

Status: Not accessible

License: None, all rights reserved

Above div doesn't exist:

	<div class="peptide_wrap_s10_right_inner">
        	<div id="DownloadOption">
			<img id="imgdownload" style="margin-left: 60px;" title="Please wait while Download options loads"
                         alt="Please wait while Download options loads" src="http://sod-a.rsc-cdn.org/pubs.rsc.org/content/NewImages/Ajax-GA-Loader.gif" />
                </div>
	[…]
	</div>


