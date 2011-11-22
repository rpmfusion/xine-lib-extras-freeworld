
%define plugin_abi  1.29

Name:           xine-lib-extras-freeworld
Summary:        Extra codecs for the Xine multimedia library
Version:        1.1.20
Release:        1%{?dist}
License:        GPLv2+
Group:          System Environment/Libraries
URL:            http://xinehq.de/
Source0:        http://downloads.sourceforge.net/xine/xine-lib-%{version}.tar.xz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0:         xine-lib-1.1.19-no_autopoint.patch
Patch1:         xine-lib-1.1.4-optflags.patch
# fix system libdvdnav support to also link libdvdread
# otherwise, we get unresolved symbols in the spudec plugin
Patch2:         xine-lib-1.1.20-link-libdvdread.patch

## upstreamable patches

BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
BuildRequires:  gawk
BuildRequires:  faad2-devel
BuildRequires:  ffmpeg-devel >= 0.4.9-0.22.20060804
BuildRequires:  a52dec-devel
BuildRequires:  libmad-devel
BuildRequires:  libdca-devel
# X11 for DXR3 output (#1258), libXt-devel needed in FC5
BuildRequires:  libXt-devel
BuildRequires:  libXext-devel
BuildRequires:  libXinerama-devel
# vcdimager reads and writes MPEG
BuildRequires:  vcdimager-devel >= 0.7.23
BuildRequires:  sed
BuildRequires:  libdvdnav-devel
BuildRequires:  libdvdread-devel
# Obsolete DXR3 deps, better handled by ffmpeg
BuildConflicts: rte-devel
BuildConflicts: libfame-devel

Requires:       vcdimager >= 0.7.23
Requires:       xine-lib(plugin-abi)%{?_isa} = %{plugin_abi}

# obsolete old livna package
Provides:       xine-lib-extras-nonfree = %{version}-%{release}
Obsoletes:      xine-lib-extras-nonfree < 1.1.15-2

# obsolete old freshrpms package
Provides:       xine-lib-moles = %{version}-%{release}
Obsoletes:      xine-lib-moles < 1.1.15-2

%description
This package contains extra codecs for the Xine multimedia library.  These
are free and opensource but left out of the official Fedora repository for 
one reason or another.  Once installed, applications using the xine library
will automatically regcognize and use these additional codecs.


%prep
%setup -q -n xine-lib-%{version}

%patch0 -p1 -b .no_autopoint
# extra work for to omit old libtool-related crud
rm -f configure ltmain.sh libtool m4/libtool.m4 m4/ltoptions.m4 m4/ltversion.m4
%patch1 -p1 -b .optflags
%patch2 -p1 -b .link-libdvdread

./autogen.sh noconfig


%build
# Keep order of options the same as in ./configure --help for easy maintenance
%configure \
    --disable-dependency-tracking \
    --enable-ipv6 \
    --disable-opengl \
    --disable-xvmc \
    --disable-aalib \
    --disable-mng \
    --disable-gnomevfs \
    --disable-gdkpixbuf \
    --disable-samba \
    --with-external-ffmpeg \
    --without-caca \
    --without-sdl \
    --without-speex \
    --without-libflac \
    --with-external-a52dec \
    --with-external-libmad \
    --without-imagemagick \
    --without-freetype \
    --without-alsa \
    --without-esound \
    --without-arts \
    --with-external-dvdnav \
    --with-external-libfaad \
    --with-external-libdts

make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Removing useless files
rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_datadir}
rm -rf %{buildroot}%{_libdir}/lib*
rm -rf %{buildroot}%{_libdir}/pkgconfig

#xineplug_dmx_mpeg
#xineplug_dmx_mpeg_block
#xineplug_dmx_mpeg_ts
#xineplug_dmx_mpeg_elem
#xineplug_dmx_mpeg_pes
#xineplug_dmx_yuv4mpeg2

# Plugins - credits go to the SuSE RPM maintainer, congrats
cat > plugins << EOF
#
# libmad and MPEG related plugins
xineplug_decode_mad
xineplug_decode_mpeg2
xineplug_inp_vcd
xineplug_inp_vcdo
#
# NES Music File Format. free ??
xineplug_decode_nsf
#
# AC3
xineplug_decode_a52
#
# likely to have legal problems
xineplug_decode_dvaudio
xineplug_decode_faad
xineplug_decode_ff
xineplug_dmx_asf
#
# dxr3 plugin is more featureful with mpeg
xineplug_decode_dxr3_spu
xineplug_decode_dxr3_video
xineplug_vo_out_dxr3
#
# DVD reading
xineplug_inp_dvd
#
# http://www.videolan.org/dtsdec.html
xineplug_decode_dts
#
# MMS
xineplug_inp_mms
#
# Don't build on the free rpm
post/xineplug_post_planar
post/xineplug_post_tvtime
#
EOF

DIR="$(ls -1d %{buildroot}%{_libdir}/xine/plugins/*)"
mv $DIR $DIR.temp
mkdir -p $DIR/post
grep -v ^# plugins | while read i; do
  mv $DIR.temp/$i.so $DIR/$i.so
done
rm -rf $DIR.temp


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc doc/README.dxr3 doc/README.network_dvd
%{_libdir}/xine/plugins/%{plugin_abi}/xineplug_*.so
%{_libdir}/xine/plugins/%{plugin_abi}/post/xineplug_*.so


%changelog
* Tue Nov 22 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.1.20-1
- update to 1.1.20 (matches Fedora xine-lib)
- use .xz tarball
- drop old conditionals
- drop unused deepbind patch
- use the system libdvdnav (and libdvdread) instead of the bundled one
- fix system libdvdnav support to also link libdvdread
- run autogen.sh in %%prep, don't patch generated files
- drop ffmpeg08 patch, fixed upstream
- update configure flags (drop nonexistent ones, fix renamed ones)

* Thu Sep 29 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.1.19-3
- fix build with FFmpeg 0.8 (#1957)

* Mon Sep 26 2011 Nicolas Chauvet <kwizart@gmail.com> - 1.1.19-2
- Rebuilt for FFmpeg-0.8

* Sun Jul 25 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.19-1
- xine-lib-1.1.19

* Sun Mar 07 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.18.1-1
- xine-lib-1.1.18.1

* Tue Mar 02 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.18-3
- get missing/upstream compat.c

* Mon Mar 01 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.18-2
- better dxr3_no_compat_c.patch (s/compat.c/compat.h/)

* Wed Feb 24 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.18-1
- xine-lib-1.1.18, plugin-abi 1.28

* Fri Jan 22 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.1.17-2
- rebuild (libcdio)

* Wed Dec 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.17-1
- xine-lib-1.1.17, plugin-abi 1.27

* Thu Jul 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.3-2
- rebuild (DirectFB)

* Fri Apr 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.3-1
- xine-lib-1.1.16.3, plugin-abi 1.26

* Fri Mar 27 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.2-4
- rebuild (faad)

* Mon Mar 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.2-3
- Requires: xine-lib(plugin-abi)%%{?_isa} = ...

* Thu Mar 12 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.2-2
- respin for newer rpm/hashes

* Tue Feb 10 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.2-1
- xine-lib-1.1.16.2

* Fri Jan 23 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16.1-1
- xine-lib-1.1.16.1

* Sun Jan 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16-3
- drop deepbind patch
- --with-external-libfaad (fedora)

* Thu Jan 08 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16-2
- drop ffmpeg_api patch (not needed)
- internal_ffmpeg patch

* Wed Jan 07 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16-1
- xine-lib-1.1.16

* Wed Dec 17 2008 Rex Dieter <rdieter@fedoraproject.org> - 1.1.15-5
- ffmpeg bits_per_sample patch 

* Thu Sep 25 2008 Rex Dieter <rdieter@fedoraproject.org> - 1.1.15-4
- Obsoletes: xine-lib-moles < 1.1.15-2

* Thu Sep 25 2008 Rex Dieter <rdieter@fedoraproject.org> - 1.1.15-3
- drop "nonfree" verbage from summary/description

* Thu Sep 04 2008 Rex Dieter <rdieter@fedoraproject.org> - 1.1.15-2
- bump Obsoletes: xine-lib-extras-nonfree
- spec cosmetics

* Mon Aug 18 2008 Rex Dieter <rdieter@fedoraproject.org> - 1.1.15-1
- 1.1.15

* Sun Aug 10 2008 Thorsten Leemhuis <fedora at leemhuis.info> - 1.1.12-2
- rename to xine-lib-extras-freeworld
- add provides and obsoletes for packages from livna and freshrpms

* Wed Apr 16 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.12-1
- 1.1.12.

* Sun Mar 30 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.11.1-1
- 1.1.11.1.
- Require xine-lib(plugin-abi) instead of xine-lib.

* Wed Mar 19 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.11-1
- 1.1.11.
- Specfile cleanups.

* Fri Feb  8 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.10.1-2
- Be explicit about using internal dvdnav for now.

* Fri Feb  8 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.10.1-1
- 1.1.10.1.

* Sun Jan 27 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.10-2
- Move spu, spucc, and spucmml decoders to main xine-lib.

* Sun Jan 27 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.10-1
- 1.1.10 (security update).

* Sat Jan 12 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.9.1-1
- 1.1.9.1 (security update).

* Sun Jan  6 2008 Ville Skyttä <ville.skytta at iki.fi> - 1.1.9-1
- 1.1.9.

* Wed Dec  5 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.8-6
- Rebuild to fix crashes with new libdvdnav.

* Sat Nov 24 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 1.1.8-5
- rebuilt

* Tue Nov 06 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 1.1.8-4
- fix building against latest ffmpeg

* Tue Nov 06 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 1.1.8-3
- rebuild

* Sat Sep  1 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.8-2
- BuildRequires: gawk

* Sat Sep  1 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.8-1
- 1.1.8, "open" patch applied upstream.

* Tue Aug 14 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.7-2
- Protect "open" for glibc 2.6.90 and -D_FORTIFY_SOURCE=2.
- License: GPLv2+

* Thu Jun  7 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.7-1
- 1.1.7.

* Wed Apr 18 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.6-1
- 1.1.6.

* Wed Apr 11 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.5-1
- 1.1.5, GSM 06.10 decoder moved to Fedora xine-lib.

* Wed Jan 31 2007 Ville Skyttä <ville.skytta at iki.fi> - 1.1.4-1
- 1.1.4.

* Tue Dec 19 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.3-4
- Use system libdca.

* Sun Dec 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.3-3
- Fix build time libpostproc version check.

* Sun Dec 17 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.3-2
- Don't run autotools during build.

* Sat Dec  9 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.3-1
- 1.1.3, require same version of xine-lib.

* Mon Nov  6 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.2-5
- Build DXR3 output with X11 (#1258).
- Explicitly disable building aRts stuff.

* Fri Nov 03 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.1.2-4
- require xine-lib >= 1.1.2-17 to ease transition

* Wed Nov  1 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.2-3
- Explicitly disable quite a few features we don't want in this package.
- Drop multilib devel patch, it's a no-op here.

* Wed Nov 01 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.1.2-2
- remove vdr stuff (unmaintained)

* Tue Oct 31 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.1.2-1
- initial rpm as xine-extras-nonfree

* Fri Aug 18 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.1.2-11
- Apply patch from upstream CVS to take advantage of new ffmpeg goodies.
