# TODO:
# - external dvdnav - not compatible as of 1.1.11 and 4.1.1

%define abiver  1.25

%if 0%{?fedora} > 6
%define _with_external_ffmpeg --with-external-ffmpeg
%define _with_external_libfaad --with-external-libfaad
%endif

Name:           xine-lib-extras-freeworld
Summary:        Extra codecs for the Xine multimedia library
Version:        1.1.16
Release:        3%{?dist}
License:        GPLv2+
Group:          System Environment/Libraries
URL:            http://xinehq.de/
Source0:        http://downloads.sourceforge.net/xine/xine-lib-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0: xine-lib-1.1.3-optflags.patch
Patch6: xine-lib-1.1.1-deepbind-939.patch
# http://hg.debian.org/hg/xine-lib/xine-lib?cmd=changeset;node=c20ec3a8802d8f71d4ad9dc26a413716efe2d71a;style=raw
Patch100: xine-lib-1.1.16-internal_ffmpeg.patch

BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
BuildRequires:  gawk
%if 0%{?_with_external_libfaad:1}
BuildRequires:  faad2-devel
%endif
%if 0%{?_with_external_ffmpeg:1}
BuildRequires:  ffmpeg-devel >= 0.4.9-0.22.20060804
# HACKS to workaround missing deps in ffmpeg-devel
# BuildRequires:  dirac-devel libraw1394-devel libtheora-devel libvorbis-devel
%endif
BuildRequires:  a52dec-devel
BuildRequires:  libmad-devel
BuildRequires:  libdca-devel
# X11 for DXR3 output (#1258), libXt-devel needed in FC5
BuildRequires:  libXt-devel
BuildRequires:  libXext-devel
BuildRequires:  libXinerama-devel
# vcdimager reads and writes MPEG
BuildRequires:  vcdimager-devel >= 0.7.23
# Obsolete DXR3 deps, better handled by ffmpeg
BuildConflicts: rte-devel
BuildConflicts: libfame-devel

Requires:       vcdimager >= 0.7.23
Requires:       xine-lib(plugin-abi) = %{abiver}

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
touch -r m4/optimizations.m4 m4/optimizations.m4.stamp
%patch0 -p1 -b .optflags
touch -r m4/optimizations.m4.stamp m4/optimizations.m4
# when compiling with external ffmpeg and internal libfaad #939.
#patch6 -p1 -b .deepbind

%patch100 -p1 -b .internal_ffmpeg

# Avoid standard rpaths on lib64 archs:
sed -i -e 's|"/lib /usr/lib\b|"/%{_lib} %{_libdir}|' configure


%build
# Keep order of options the same as in ./configure --help for easy maintenance
%configure \
    --disable-dependency-tracking \
    --enable-ipv6 \
    --disable-opengl \
    --disable-xvmc \
    --disable-aalib \
    --disable-caca \
    --disable-sdl \
    --disable-rte \
    --disable-libfame \
    --disable-speex \
    --disable-flac \
    --disable-mng \
    --disable-imagemagick \
    --disable-freetype \
    --disable-alsa \
    --disable-esd \
    --disable-arts \
    --disable-gnomevfs \
    --disable-gdkpixbuf \
    --disable-samba \
    %{?_with_external_ffmpeg} \
    --with-external-a52dec \
    --with-external-libmad \
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
%{_libdir}/xine/plugins/%{abiver}/xineplug_*.so
%{_libdir}/xine/plugins/%{abiver}/post/xineplug_*.so


%changelog
* Sun Jan 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.1.16-3
- drop deepbind patch
- --with-external-libfaad 

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
