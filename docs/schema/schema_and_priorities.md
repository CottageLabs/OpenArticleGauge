Examples and location of licensing information for specific publishers
======================================================================

Outline
-------

The purpose of this document is to identify the source of licensing information in the html pages provided by different scholarly publishers and to provide a test set of documents associated with authoritative statements of the license status.

The HTML documents are the result of dereferencing specified DOIs. They therefore vary as to whether they contain abstracts or full text papers. For each publisher there are multiple examples provided that have different license status.

BioMedCentral
-------------

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

PLOS
____

The majority of PLOS articles are made available under a Creative Commons Attribution license with no version specified in the human readable text. Some articles, particularly older ones, have non-standard license text. There are also at least three variants licenses deployed, ccZero for work exclusive authored by US Government Employess, the UK Open Government License, and a generic WHO License which specifies non-commercial terms.

###Examples
####A standard CC BY article

DOI: 10.1371/journal.pbio.1001461

Dereferenced URL: http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461

Status: Open Access
License: CC BY

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


Below here still needs work!
----------------------------


OUP:
HTML:
Mixed publisher, examples include:

From Bioinformatics, difference between a non-OA...
<ul class="copyright-statement">
                  <li class="fn" id="copyright-statement-1">© The Author 2012. Published by Oxford University Press. All rights reserved. For Permissions, please e-mail: journals.permissions@oup.com</li>
               </ul>

…and an OA article...

<ul class="copyright-statement">
                  <li class="fn" id="copyright-statement-1">© The Author 2012. Published by Oxford University Press.</li>
               </ul>
               <div class="license" id="license-1">
                  <p id="p-2">This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),
                     which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.
                  </p>
               </div>

From NAR, the difference between CC BY-NC:
<ul class="copyright-statement">
                  <li class="fn" id="copyright-statement-1">© The Author(s) 2012. Published by Oxford University Press.</li>
               </ul>
               <div class="license" id="license-1">
                  <p id="p-1">This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0),
                     which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is
                     properly cited.
                  </p>
               </div>

and CC BY:
<ul class="copyright-statement">
                  <li class="fn" id="copyright-statement-1">© The Author(s) 2012. Published by Oxford University Press.</li>
               </ul>
               <div class="license" id="license-1">
                  <p id="p-1">This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),
                     which permits unrestricted, distribution, and reproduction in any medium, provided the original work is properly cited.
                  </p>
               </div>

No other divs with class="license" apparently



