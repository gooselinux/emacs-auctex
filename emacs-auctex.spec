# If the emacs-el package has installed a pkgconfig file, use that to determine
# install locations and Emacs version at build time, otherwise set defaults.
%if %($(pkg-config emacs) ; echo $?)
%define emacs_version 22.1
%define emacs_lispdir %{_datadir}/emacs/site-lisp
%define emacs_startdir %{emacs_lispdir}/site-start.d
%else
%define emacs_version %(pkg-config emacs --modversion)
%define emacs_lispdir %(pkg-config emacs --variable sitepkglispdir)
%define emacs_startdir %(pkg-config emacs --variable sitestartdir)
%endif

# AucTeX includes preview-latex which allows previeweing directly in the Emacs
# buffer. This makes use of preview.sty, a LaTeX class, which is also included
# with AucTex preview-latex can either use a privately installed copy of
# preview.sty, or it can use one installed in the system texmf tree. If the
# following is set to 1, an add-on LaTeX package will be created which installs
# into the system texmf tree, and preview-latex will use that. However, TeXLive
# already includes preview.sty and so this may not be desireable -- setting the
# following value to 0 means that preview-latex/AucTeX will use a privately
# installed copy of preview.sty.
%define separate_preview 1

Summary: 	Enhanced TeX modes for Emacs
Name: 		emacs-auctex
Version: 	11.85
Release: 	10%{?dist}
License: 	GPLv3+
Group: 		Applications/Editors
URL: 		http://www.gnu.org/software/auctex/
Obsoletes: 	auctex
Provides: 	auctex
Conflicts: 	emacspeak < 18
Requires: 	emacs(bin) >= %{emacs_version}
Requires:	ghostscript dvipng
Requires:	tex(latex) tex(dvips)
Requires(pre): 	/sbin/install-info 
Requires(post): /sbin/install-info
%if %{separate_preview}
Requires: 	tex-preview = %{version}-%{release}
%endif

Source0: 	ftp://ftp.gnu.org/pub/gnu/auctex/auctex-%{version}.tar.gz
BuildArch: 	noarch
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: 	emacs emacs-el texlive-latex texinfo-tex ghostscript

%description 
AUCTeX is an extensible package that supports writing and formatting
TeX files for most variants of Emacs.

AUCTeX supports many different TeX macro packages, including AMS-TeX,
LaTeX, Texinfo and basic support for ConTeXt.  Documentation can be
found under /usr/share/doc, e.g. the reference card (tex-ref.pdf) and
the FAQ. The AUCTeX manual is available in Emacs info (C-h i d m
AUCTeX RET). On the AUCTeX home page, we provide manuals in various
formats.

AUCTeX includes preview-latex support which makes LaTeX a tightly
integrated component of your editing workflow by visualizing selected
source chunks (such as single formulas or graphics) directly as images
in the source buffer.

This package is for GNU Emacs.

%package el
Summary: 	Elisp source files for %{name}
Group: 		Applications/Editors
Requires: 	%{name} = %{version}-%{release}

%description el
This package contains the source Elisp files for AUCTeX for Emacs.

%package doc
Summary:	Documentation in various formats for AUCTeX
Group:		Documentation

%description doc
Documentation for the AUCTeX package for emacs in various formats,
including HTML and PDF.

%if %{separate_preview}
%package -n tex-preview
Summary: 	Preview style files for LaTeX
Group: 		Applications/Publishing
Requires: 	tex(latex)
Obsoletes:	tetex-preview
Provides:	tetex-preview

%description -n tex-preview 
The preview package for LaTeX allows for the processing of selected
parts of a LaTeX input file.  This package extracts indicated pieces
from a source file (typically displayed equations, figures and
graphics) and typesets with their base point at the (1in,1in) magic
location, shipping out the individual pieces on separate pages without
any page markup.  You can produce either DVI or PDF files, and options
exist that will set the page size separately for each page.  In that
manner, further processing (as with Ghostscript or dvipng) will be
able to work in a single pass.

The main purpose of this package is the extraction of certain
environments (most notably displayed formulas) from LaTeX sources as
graphics. This works with DVI files postprocessed by either Dvips and
Ghostscript or dvipng, but it also works when you are using PDFTeX for
generating PDF files (usually also postprocessed by Ghostscript).

The tex-preview package is generated from the AUCTeX package for 
Emacs.
%endif

%prep
%setup -q -n auctex-%{version}

%build
%if %{separate_preview}
%configure --with-emacs 
%else
%configure --with-emacs --without-texmf-dir
%endif

make

# Build documentation in various formats
pushd doc
make extradist
popd

# Fix some encodings
iconv -f ISO-8859-1 -t UTF8 RELEASE > RELEASE.utf8 && touch -r RELEASE RELEASE.utf8 && mv RELEASE.utf8 RELEASE

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{emacs_startdir}
make DESTDIR=%{buildroot} install
rm -rf %{buildroot}%{_var}

# Remove /usr/share/doc/auctex directory from buildroot since we don't want doc
# files installed here
rm -rf %{buildroot}%{_docdir}/auctex

%clean
rm -rf %{buildroot}

%post
/sbin/install-info %{_infodir}/auctex.info %{_infodir}/dir 2>/dev/null || :
/sbin/install-info %{_infodir}/preview-latex.info %{_infodir}/dir 2>/dev/null || :

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/auctex.info %{_infodir}/dir 2>/dev/null || :
  /sbin/install-info --delete %{_infodir}/preview-latex.info %{_infodir}/dir 2>/dev/null || :
fi

%if %{separate_preview}
%post -n tex-preview
/usr/bin/texhash > /dev/null 2>&1 || :

%postun -n tex-preview
/usr/bin/texhash > /dev/null 2>&1 || :
%endif

%files
%defattr(-,root,root,-)
%doc RELEASE COPYING README TODO FAQ CHANGES
%doc %{_infodir}/*.info*
%exclude %{_infodir}/dir
%{emacs_startdir}/*
%dir %{emacs_lispdir}/auctex
%dir %{emacs_lispdir}/auctex/style
%{emacs_lispdir}/auctex/*.elc
%{emacs_lispdir}/auctex/style/*.elc
%{emacs_lispdir}/auctex/.nosearch
%{emacs_lispdir}/auctex/style/.nosearch
%{emacs_lispdir}/auctex/images
%{emacs_lispdir}/tex-site.el
%if !%{separate_preview}
%{emacs_lispdir}/auctex/latex
%{emacs_lispdir}/auctex/doc
%endif

%files el
%defattr(-,root,root,-)
%{emacs_lispdir}/auctex/*.el
%{emacs_lispdir}/auctex/style/*.el

%if %{separate_preview}
%files -n tex-preview
%defattr(-,root,root,-)
%{_datadir}/texmf/tex/latex/preview
%{_datadir}/texmf/doc/latex/styles
%endif

%files doc
%defattr(-,root,root,-)
%doc doc/*.{dvi,ps,pdf}
%doc doc/html

%changelog
* Thu Jan 07 2010 Daniel Novotny <dnovotny@redhat.com> 11.85-10
- fixed file permissions rpmlint error in spec

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 11.85-9.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 11.85-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 11.85-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Feb 24 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-7
- Add Requires for dvipng

* Sat Feb 16 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-6
- Preserve timestamp of RELEASE when converting to UTF8

* Wed Feb 13 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-5
- Re-add creation of emacs_startdir

* Tue Feb 12 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-4
- Remove BuildRequires for pkgconfig - not needed
- Clean out uneeded creation of site start directory
- Remove /usr/share/doc/auctex directory from buildroot

* Tue Feb 12 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-3
- Bump release and rebuild - had forgotten to upload the new sources

* Tue Feb 12 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-2
- Add BuilddRequires for pkgconfig

* Tue Feb 12 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.85-1
- Update to version 11.85
- Change license to GPLv3+ accordingly

* Wed Jan 23 2008 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-7
- tex-preview no longer Requires ghostscript (#429811)
- Use virtual provides for tex(latex) etc.

* Tue Dec 25 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-6
- Add Obsolotes and Provides for tetex-preview to tex-preview (#426758)

* Sun Dec 23 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-5
- Enable building of separate tex-preview package
- Remove a few residual tetex references

* Sun Dec 16 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-4
- Add macros for automatic detection of Emacs version, site-lisp directory etc
- Make building of tex-preview subpackage optional, and disable for now
- Adjust Requires and BuildRequires for texlive
- Remove auctex-init.el since not needed
- Make RELEASE utf8

* Sat Aug  4 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-3
- Clarify license version
- Correct version and release requirement for the el package

* Sat Jan 13 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-2
- Update BuildRequires for texinfo-tex package

* Sat Jan 13 2007 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.84-1
- Update to version 11.84
- Build all documentation and package in a -doc package

* Mon Aug 28 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-7
- Bump release for FC-6 mass rebuild

* Sun Jun 18 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-6
- Remove debug patch entry

* Sun Jun 18 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-5
- Bump release

* Sun Jun 18 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-4
- Bump release

* Sun Jun 18 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-3
- Sync with FC-5 spec file which includes the following changes
- No longer use makeinstall macro
- No longer specify texmf-dir, tex-dir for configure
- Main package now owns the site-lisp auctex and styles directories
- Place preview.dvi in correct directory, and have tetex-preview own
  it
- General cleanups

* Sat Jun 10 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-4
- Bump release

* Sat Jun 10 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-3
- Bump release. Wrap descriptions at column 70.

* Sat Jun 10 2006 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 11.83-1
- Update to 11.83
- Add specific release requirement to tetex-preview Requires of main package

* Wed May 24 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-12
- Bump version number.

* Wed May 24 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-11
- Fix up whitespace for Ed. Bump version number.

* Thu May 18 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-9
- Split out tetex-preview subpackage
- Split out source elisp files
- Update package descriptions

* Mon May  1 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-8
- Add tetex-latex to BuildRequires

* Mon May  1 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-7
- Add ghostscript to Requires and BuildRequires

* Mon May  1 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-6
- Leave .nosearch file in styles directory - this directory shouldn't be in the load-path

* Mon May  1 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-5
- Move installation of the preview style files out of the texmf tree for now

* Mon Apr 24 2006 Jonathan Underwood <jonathan.underwood@gmail.com> - 11.82-4
- Added preview-latex
- Removed INSTALL document from package (not necessary)
- Clean up generation of startup files from spec file

* Thu Apr 20 2006 Ed Hill <ed@eh3.com> - 11.82-3
- fix startup file per bug# 189488

* Sun Apr  9 2006 Ed Hill <ed@eh3.com> - 11.82-2
- rebuild

* Sun Apr  9 2006 Ed Hill <ed@eh3.com> - 11.82-1
- update to 11.82

* Fri Sep 30 2005 Ed Hill <ed@eh3.com> - 11.81-2
- fix stupid tagging mistake

* Fri Sep 30 2005 Ed Hill <ed@eh3.com> - 11.81-1
- update to 11.81
- disable preview for now since it needs some packaging work

* Tue Sep  6 2005 Ed Hill <ed@eh3.com> - 11.55-5
- bugzilla 167439

* Tue Aug  9 2005 Ed Hill <ed@eh3.com> - 11.55-4
- call it BuildArch

* Tue Aug  9 2005 Ed Hill <ed@eh3.com> - 11.55-3
- add Requires and BuildRequires

* Mon Aug  8 2005 Ed Hill <ed@eh3.com> - 11.55-2
- modify for acceptance into Fedora Extras

* Fri Jan 21 2005 David Kastrup <dak@gnu.org>
- Conflict with outdated Emacspeak versions

* Fri Jan 14 2005 David Kastrup <dak@gnu.org>
- Install and remove auctex.info, not auctex

* Thu Aug 19 2004 David Kastrup <dak@gnu.org>
- Change tex-site.el to overwriting config file mode.  New naming scheme.

* Mon Aug 16 2004 David Kastrup <dak@gnu.org>
- Attempt a bit of SuSEism.  Might work if we are lucky.

* Sat Dec  7 2002 David Kastrup <David.Kastrup@t-online.de>
- Change addresses to fit move to Savannah.

* Mon Apr 15 2002 Jan-Ake Larsson <jalar@imf.au.dk>
- Adjusted TeX-macro-global and put autoactivation in preinstall
  script so that it can be chosen at install time.

* Tue Feb 19 2002 Jan-Ake Larsson <jalar@imf.au.dk>
- Added site-start.el support

* Sat Feb 16 2002 Jan-Ake Larsson <jalar@imf.au.dk>
- Prerelease 11.11
