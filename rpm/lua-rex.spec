Name:           tarantool-lrexlib
# During package building {version} is overwritten by Packpack with
# VERSION. It is set to major.minor.patch.number_of_commits_above_last_tag.
# major.minor.patch tag and number of commits above are taken from the
# github repository: https://github.com/tarantool/lrexlib
Version:        2.9.0
Release:        1%{?dist}
Summary:        Regular expression handling library for Lua

Group:          Development/Libraries
License:        MIT
URL:            https://github.com/tarantool/lrexlib
Source0:        lrexlib-%{version}.tar.gz

%description
Lrexlib are bindings of six regular expression library APIs (POSIX, PCRE, PCRE2,
Oniguruma, Tre and GNU) to Lua.

%package pcre
Summary: Lua binding of PCRE library
BuildRequires:  pcre-devel
BuildRequires:  pkgconfig
BuildRequires:  tarantool-devel >= 1.9.0.0
BuildRequires:  luarocks
Requires:       tarantool >= 1.9.0.0
Requires:       pcre
Provides:       tarantool-lrexlib-pcre = %{version}

%description pcre
Binding of PCRE library

%package pcre2
Summary: Lua binding of PCRE-2 library
BuildRequires:  pcre2-devel
BuildRequires:  pkgconfig
BuildRequires:  tarantool-devel >= 1.9.0.0
BuildRequires:  luarocks
Requires:       tarantool >= 1.9.0.0
Requires:       pcre2
Provides:       tarantool-lrexlib-pcre2 = %{version}

%description pcre2
Binding of PCRE2 library

%package posix
Summary: Lua binding of POSIX library
BuildRequires:  pkgconfig
BuildRequires:  tarantool-devel >= 1.9.0.0
BuildRequires:  luarocks
Requires:       tarantool >= 1.9.0.0
Provides:       tarantool-lrexlib-posix = %{version}

%description posix
Binding of POSIX library

%package gnu
Summary: Lua binding of GNU library
BuildRequires:  pkgconfig
BuildRequires:  tarantool-devel >= 1.9.0.0
BuildRequires:  luarocks
Requires:       tarantool >= 1.9.0.0
Provides:       tarantool-lrexlib-gnu = %{version}

%description gnu
Binding of GNU library

%package oniguruma
Summary: Lua binding of Oniguruma library
BuildRequires:  oniguruma-devel
BuildRequires:  pkgconfig
BuildRequires:  tarantool-devel >= 1.9.0.0
BuildRequires:  luarocks
Requires:       oniguruma
Requires:       tarantool >= 1.9.0.0
Provides:       tarantool-lrexlib-oniguruma = %{version}

%description oniguruma
Binding of Oniguruma library

#%package tre
#Summary: Lua binding of TRE library
#BuildRequires:  tre-devel >= 0.8.0
#BuildRequires:  pkgconfig
#BuildRequires:  tarantool-devel >= 1.9.0.0
#BuildRequires:  luarocks
#Requires:       tre
#Requires:       tarantool >= 1.9.0.0
#Provides:       tarantool-lrexlib-tre = %{version}

#%description tre
#Binding of TRE library

%prep
%setup -q -n lrexlib-%{version}

%build
tarantool mkrockspecs.lua lrexlib %{version}
ls
mkdir tree
for i in pcre pcre2 posix oniguruma gnu; do
	TMP=$PWD/tmp luarocks --local --tree=./tree make lrexlib-$i-%{version}-1.rockspec \
	CFLAGS="%{optflags} -fPIC -DLUA_COMPAT_APIINTCASTS -I%{_prefix}/include/tarantool" \
	PCRE_LIBDIR=%{_libdir} PCRE2_LIBDIR=%{_libdir} ONIG_LIBDIR=%{_libdir} \
	TRE_LIBDIR=%{_libdir} TRE_INCDIR=/usr/include
done

%install
install -d %{buildroot}%{_datadir}

# Note that Lua is not used for building, as libraries are built against
# tarantool headers (-I%{_prefix}/include/tarantool in make command above).
#
# Luarocks detects lua(abi) lib (which is in requires of luarocks package)
# and use it's version to name directories with built libs. On different
# OS luarocks package requires different versions of lua(abi), so the
# directories would have different names. To handle it we use conditional
# statements (see below). Consider example:
#
# Centos (rhel):   tree/lib64/lua/5.1/some.so
# Fedora (fedora): tree/lib64/lua/5.3/some.so

%if 0%{?rhel}
    LUA_VER=5.1
%endif

%if 0%{?fedora}
    LUA_VER=5.3
%endif

# On different OS luarocks names directories with built libs differently.
# Centos (rhel) 6:    tree/lib/lua/5.1/some.so
# Centos (rhel) 7:    tree/lib64/lua/5.1/some.so
# Fedora (fedora) 26: tree/lib64/lua/5.3/some.so
# Fedora (fedora) 27: tree/lib64/lua/5.3/some.so
# To handle this the following conditional statement is used.

LIB=%{_lib}

%if 0%{?rhel}
    %if 0%{?rhel} <= 6
        LIB="lib"
    %endif
%endif

mkdir -p %{buildroot}%{_libdir}/tarantool
for i in pcre pcre2 posix gnu onig; do
    cp -P tree/${LIB}/lua/${LUA_VER}/rex_$i.so %{buildroot}%{_libdir}/tarantool/rex_$i.so
done

%check
make %{?_smp_mflags} test

%files pcre
%{_libdir}/tarantool/rex_pcre.so

%files pcre2
%{_libdir}/tarantool/rex_pcre2.so

%files posix
%{_libdir}/tarantool/rex_posix.so

%files gnu
%{_libdir}/tarantool/rex_gnu.so

%files oniguruma
%{_libdir}/tarantool/rex_onig.so

#%files tre
#%{_libdir}/tarantool/rex_tre.so

%changelog
* Tue Jul 10 2018 Ivan Koptelov <ivan.koptelov@tarantool.org> - 2.9.0-1
- Change .spec in order to:
    - Use it with packpack
    - Build separate package for every flavour (pcre, pcre2, posix, etc)
    - Build packages against tarantool instead of lua
- Note: tre flavour is disabled due to there is no suitable package in
  standard repos and using prebuild.sh cause the unknown error in packpack

* Tue Aug 29 2017 Lubomir Rintel <lkundrak@v3.sk> - 2.8.0-1
- Update to a latest version

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Oct 30 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.7.2-13
- Rebuild for oniguruma 6.1.1

* Mon Jul 18 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.7.2-12
- Rebuild for oniguruma 6

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 14 2015 Ville Skyttä <ville.skytta@iki.fi> - 2.7.2-9
- Mark LICENSE as %%license, don't ship .gitignore

* Thu Jan 15 2015 Tom Callaway <spot@fedoraproject.org> - 2.7.2-8
- rebuild for lua 5.3

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Oct 24 2013 Lubomir Rintel <lkundrak@v3.sk> - 2.7.2-5
- Bulk sad and useless attempt at consistent SPEC file formatting

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun  4 2013 Tom Callaway <spot@fedoraproject.org>	- 2.7.2-3
- use lua(abi) for Requires. A B I.

* Mon Jun  3 2013 Tom Callaway <spot@fedoraproject.org> - 2.7.2-2
- use lua(api) for Requires

* Sun May 12 2013 Tom Callaway <spot@fedoraproject.org> - 2.7.2-1
- update to 2.7.2

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 2.4.0-8
- Rebuild against PCRE 8.30

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 23 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-3
- Compile shared library as PIC

* Wed Dec 17 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-2
- Add doc directory to documentation
- Allow parallel make runs

* Tue Dec 16 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-1
- Initial packaging
