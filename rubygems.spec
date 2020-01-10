%define gem_dir %(ruby -rrbconfig -e 'puts File::expand_path(File::join(RbConfig::CONFIG["sitedir"],"..","gems"))')
%define rb_ver %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["ruby_version"]')
%define gem_home %{gem_dir}/%{rb_ver}
%define ruby_sitelib %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["sitelibdir"]')

%define repoid 70696

Summary: The Ruby standard for packaging ruby libraries
Name: rubygems
Version: 1.3.7
Release: 4%{?dist}
Group: Development/Libraries
# No GPL version is specified.
License: Ruby or GPL+
URL: http://rubyforge.org/projects/rubygems/
Source0: http://rubyforge.org/frs/download.php/%{repoid}/rubygems-%{version}.tgz
Patch0: rubygems-1.3.7-noarch-gemdir.patch

# Fix algorithmic complexity vulnerability (CVE-2013-4287).
# https://github.com/rubygems/rubygems/issues/626
Patch1: rubygems-1.8.23.1-CVE-2013-4287-algorithmic-complexity-vulnerability.patch
# Fix insecure connection to SSL repository (CVE-2012-2125, CVE-2012-2126).
# https://github.com/rubygems/rubygems/commit/c22a3b705ead93f4cb8282e6dcb2f8f330d74edd
# NOTE 1: Certificates are omitted from patch due to:
# https://github.com/rubygems/rubygems/commit/e9388de72ee5953ff061203ad387c98b2154db87
# Upstream clarification: https://github.com/rubygems/rubygems/issues/654
# NOTE 2: The ca-bundle.pem is automatically discovered on system path by OpenSLL.
Patch2: rubygems-1.8.24-CVE-2012-2125-CVE-2012-2126-Insecure-connection-to-SSL-repository.patch
# Remove regexp backtracing (CVE-2013-4363).
# https://github.com/rubygems/rubygems/commit/56d1f8c17bc81f0eb354d5099021c498a0be9b51
Patch3: rubygems-1.8.23.1-CVE-2013-4363-remove-regexp-backtracing.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
Requires: ruby(abi) = 1.8 ruby-rdoc
BuildRequires:  ruby ruby-rdoc
BuildArch: noarch
Provides: ruby(rubygems) = %{version}

%description
RubyGems is the Ruby standard for publishing and managing third party
libraries.

%prep
%setup -q
%patch0 -p1 -b .noarch
%patch1 -p1
%patch2 -p1
%patch3 -p1

# Some of the library files start with #! which rpmlint doesn't like
# and doesn't make much sense
for f in `find lib -name \*.rb` ; do
  head -1 $f | grep -q '^#!/usr/bin/env ruby' && sed -i -e '1d' $f
done

%build
# Nothing

%install
rm -rf $RPM_BUILD_ROOT
GEM_HOME=%{buildroot}/%{gem_home} \
    ruby setup.rb --prefix=/ \
        --no-rdoc --no-ri \
        --destdir=%{buildroot}/%{ruby_sitelib}/

mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}/%{ruby_sitelib}/bin/gem %{buildroot}/%{_bindir}/gem
rm -rf %{buildroot}/%{ruby_sitelib}/bin
mv %{buildroot}/%{ruby_sitelib}/lib/* %{buildroot}/%{ruby_sitelib}/.

# FIXME!!
mkdir -p $RPM_BUILD_ROOT%{gem_home}/{cache,gems,specifications,doc}


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%doc README ChangeLog
%doc History.txt
%doc GPL.txt LICENSE.txt
%dir %{gem_dir}
%dir %{gem_home}
%dir %{gem_home}/cache
%dir %{gem_home}/gems
%dir %{gem_home}/specifications
%doc %{gem_home}/doc
%{_bindir}/gem
%{ruby_sitelib}/*

%changelog
* Wed Sep 25 2013 Vít Ondruch <vondruch@redhat.com> - 1.3.7-4
- Remove regexp backtracing (CVE-2013-4363).
  - Related: rhbz#1002838.

* Wed Sep 18 2013 Vít Ondruch <vondruch@redhat.com> - 1.3.7-3
- Fix insecure connection to SSL repository (CVE-2012-2125, CVE-2012-2126).
  - Related: rhbz#1002838.

* Mon Sep 02 2013 Vít Ondruch <vondruch@redhat.com> - 1.3.7-2
- Fix algorithmic complexity vulnerability (CVE-2013-4287).
  - Resolves: rhbz#1002838.

* Mon May 17 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.7-1
- Update to 1.3.7, dropping upstreamed patch

* Wed Apr 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.6-1
- Update to 1.3.6
- Show prefix with gem contents by default as shown in --help

* Mon Sep 21 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.5-1
- Update to 1.3.5

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Nov 09 2008 Jeroen van Meeuwen <kanarip@kanarip.com> - 1.3.1-1
- New upstream version

* Tue Sep 16 2008 David Lutterkort <dlutter@redhat.com> - 1.2.0-2
- Bump release because I forgot to check in newer patch

* Tue Sep 16 2008 David Lutterkort <dlutter@redhat.com> - 1.2.0-1
- Updated for new setup.rb
- Simplified by removing conditionals that were needed for EL-4;
  there's just no way we can support that with newer rubygems

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.9.4-2
- fix license tag

* Fri Jul 27 2007 David Lutterkort <dlutter@redhat.com> - 0.9.4-1
- Conditionalize so it builds on RHEL4

* Tue Feb 27 2007 David Lutterkort <dlutter@redhat.com> - 0.9.2-1
- New version
- Add patch0 to fix multilib sensitivity of Gem::dir (bz 227400)

* Thu Jan 18 2007 David Lutterkort <dlutter@redhat.com> - 0.9.1-1
- New version; include LICENSE.txt and GPL.txt
- avoid '..' in gem_dir to work around a bug in gem installer
- add ruby-rdoc to requirements

* Tue Jan  2 2007 David Lutterkort <dlutter@redhat.com> - 0.9.0-2
- Fix gem_dir to be arch independent
- Mention dual licensing in License field

* Fri Dec 22 2006 David Lutterkort <dlutter@redhat.com> - 0.9.0-1
- Updated to 0.9.0
- Changed to agree with Fedora Extras guidelines

* Mon Jan  9 2006 David Lutterkort <dlutter@redhat.com> - 0.8.11-1
- Updated for 0.8.11

* Sun Oct 10 2004 Omar Kilani <omar@tinysofa.org> 0.8.1-1ts
- First version of the package
