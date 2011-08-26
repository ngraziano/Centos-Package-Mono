%{!?ext_man: %define ext_man .gz}
%define _prefix /opt/novell/mono
%define _sysconfdir /etc/opt/novell
%define _mandir %_datadir/man

%define llvm no
%define sgen yes

%ifnarch %ix86 x86_64
%define llvm no
%define sgen no
%endif

Name:           mono-addon-core
License:        LGPL v2.1 only
Group:          Development/Languages/Mono
Summary:        A .NET Runtime Environment
Url:            http://www.mono-project.com
Version:        2.10.5
Release:        5.1.PVPP.0
Source0:        mono-%{version}.tar.bz2
Patch0:         addon-reqprov.patch
BuildRequires:  bison
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
%if %llvm == yes
BuildRequires:  llvm-mono-devel
%endif
%if 0%{?suse_version}
BuildRequires:  fdupes
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%define _use_internal_dependency_generator 0
%define __find_provides env sh -c 'filelist=($(cat)) && { printf "%s\\n" "${filelist[@]}" | /usr/lib/rpm/find-provides && printf "%s\\n" "${filelist[@]}" | prefix=%{buildroot}%{_prefix} %{buildroot}%{_bindir}/mono-find-provides ; } | sort | uniq'
%define __find_requires env sh -c 'filelist=($(cat)) && { printf "%s\\n" "${filelist[@]}" | /usr/lib/rpm/find-requires && printf "%s\\n" "${filelist[@]}" | prefix=%{buildroot}%{_prefix} %{buildroot}%{_bindir}/mono-find-requires ; } | sort | uniq'

%description
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

%prep
%setup -q -n mono-%{version}
%patch0

%build
# These are only needed if there are patches to the runtime
#rm -f libgc/libtool.m4
#autoreconf --force --install
#autoreconf --force --install libgc
export CFLAGS=" $RPM_OPT_FLAGS -fno-strict-aliasing"
# distro specific configure options
%if %llvm == yes
export PATH=/opt/novell/llvm-mono/bin:$PATH
%endif
%configure \
  --with-sgen=%{sgen} \
%if %llvm == yes
  --enable-loadedllvm \
  --disable-system-aot \
%endif
%ifnarch %ix86 x86_64
  --disable-system-aot \
%endif
  --with-ikvm=yes \
  --with-moonlight=no
make # We are not -jN safe! %{?jobs:-j%jobs}

%install
make install DESTDIR=%buildroot
mkdir -p %buildroot%_datadir/pkgconfig
# Create a wrapper script for mono so that it can load the correct gdiplus
mv %buildroot%_bindir/mono %buildroot%_bindir/mono.bin
cat > %buildroot%_bindir/mono << EOF
#!/bin/sh
. %_bindir/mono-addon-environment.sh
exec %_bindir/mono.bin "\$@"
EOF
chmod +x %buildroot%_bindir/mono
# Create env scripts
cat > %buildroot%_bindir/mono-addon-environment.sh << EOF
# This script sets your default mono to the mono addon
# To use temporarily, source the file with: source mono-addon-environment.sh
# To use permanently, copy the file to /etc/profile.d/
export LD_LIBRARY_PATH="%_libdir:\$LD_LIBRARY_PATH"
export C_INCLUDE_PATH="%_prefix/include"
export ACLOCAL_PATH="%_datadir/aclocal"
export PKG_CONFIG_PATH="%_datadir/pkgconfig:%_libdir/pkgconfig:\$PKG_CONFIG_PATH"
export MANPATH="%_mandir:\$MANPATH"
export PATH="%_bindir:\$PATH"
PS1="[mono-addon] \$PS1"
EOF
# remove .la files (they are generally bad news)
rm -f %buildroot%_libdir/*.la
# remove Windows-only stuff
rm -rf %buildroot%_prefix/lib/mono/*/Mono.Security.Win32*
rm -f %buildroot%_libdir/libMonoSupportW.*
# remove .a files for libraries that are really only for us
rm -f %buildroot%_libdir/libMonoPosixHelper.a
rm -f %buildroot%_libdir/libikvm-native.a
rm -f %buildroot%_libdir/libmono-llvm.a
# remove libgc cruft
rm -rf %buildroot%_datadir/libgc-mono
# remove stuff that we don't package
rm -f %buildroot%_bindir/cilc
rm -f %buildroot%_mandir/man1/cilc.1*
rm -f %buildroot%_prefix/lib/mono/*/browsercaps-updater.exe*
rm -f %buildroot%_prefix/lib/mono/*/culevel.exe*
rm -f %buildroot%_prefix/lib/mono/2.0/cilc.exe*
# brp-compress doesn't search _mandir
# so we cheat it
ln -s . %buildroot%_prefix/usr
RPM_BUILD_ROOT=%buildroot%_prefix /usr/lib/rpm/brp-compress
rm %buildroot%_prefix/usr
%if 0%{?suse_version}
%fdupes %{buildroot}%{_prefix}/lib
%endif
%find_lang mcs

%clean
rm -rf %buildroot

%files -f mcs.lang
%defattr(-, root, root)
%doc AUTHORS COPYING.LIB ChangeLog NEWS README
%config %_sysconfdir/mono/2.0/machine.config
%config %_sysconfdir/mono/2.0/settings.map
%config %_sysconfdir/mono/4.0/machine.config
%config %_sysconfdir/mono/4.0/settings.map
%config %_sysconfdir/mono/config
%dir %_bindir
%dir %_datadir
%dir %_datadir/locale
%dir %_datadir/locale/*
%dir %_datadir/locale/*/LC_MESSAGES
%dir %_libdir
%dir %_libdir/pkgconfig
%dir %_mandir
%dir %_mandir/man1
%dir %_mandir/man5
%dir %_prefix
%dir %_prefix/include
%dir %_prefix/lib
%dir %_prefix/lib/mono
%dir %_prefix/lib/mono/2.0
%dir %_prefix/lib/mono/3.5
%dir %_prefix/lib/mono/4.0
%dir %_prefix/lib/mono/compat-2.0
%dir %_prefix/lib/mono/gac
%dir %_sysconfdir
%dir %_sysconfdir/mono
%dir %_sysconfdir/mono/2.0
%dir %_sysconfdir/mono/4.0
%dir /opt/novell
%_bindir/al
%_bindir/al2
%_bindir/certmgr
%_bindir/chktrust
%_bindir/csharp
%_bindir/csharp2
%_bindir/dmcs
%_bindir/gacutil
%_bindir/gacutil2
%_bindir/gmcs
%_bindir/mcs
%_bindir/mono
%_bindir/mono.bin
%_bindir/mono-addon-environment.sh
%_bindir/mono-configuration-crypto
%if %sgen == yes
%_bindir/mono-sgen
%endif
%_bindir/mono-test-install
%_bindir/mozroots
%_bindir/peverify
%_bindir/setreg
%_bindir/sn
%_libdir/libMonoPosixHelper.so*
%_libdir/libikvm-native.so
%_mandir/man1/certmgr.1%ext_man
%_mandir/man1/chktrust.1%ext_man
%_mandir/man1/csharp.1%ext_man
%_mandir/man1/gacutil.1%ext_man
%_mandir/man1/mcs.1%ext_man
%_mandir/man1/mono-configuration-crypto.1%ext_man
%_mandir/man1/mono.1%ext_man
%_mandir/man1/mozroots.1%ext_man
%_mandir/man1/setreg.1%ext_man
%_mandir/man1/sn.1%ext_man
%_mandir/man5/mono-config.5%ext_man
%_prefix/lib/mono/2.0/Commons.Xml.Relaxng.dll
%_prefix/lib/mono/2.0/CustomMarshalers.dll
%_prefix/lib/mono/2.0/I18N.West.dll
%_prefix/lib/mono/2.0/I18N.dll
%_prefix/lib/mono/2.0/ICSharpCode.SharpZipLib.dll
%_prefix/lib/mono/2.0/Microsoft.VisualC.dll
%_prefix/lib/mono/2.0/Mono.C5.dll
%_prefix/lib/mono/2.0/Mono.CSharp.dll
%_prefix/lib/mono/2.0/Mono.Cairo.dll
%_prefix/lib/mono/2.0/Mono.CompilerServices.SymbolWriter.dll
%_prefix/lib/mono/2.0/Mono.Management.dll
%_prefix/lib/mono/2.0/Mono.Posix.dll
%_prefix/lib/mono/2.0/Mono.Security.dll
%_prefix/lib/mono/2.0/Mono.Simd.dll
%_prefix/lib/mono/2.0/Mono.Tasklets.dll
%_prefix/lib/mono/2.0/OpenSystem.C.dll
%_prefix/lib/mono/2.0/System.Configuration.dll
%_prefix/lib/mono/2.0/System.Core.dll
%_prefix/lib/mono/2.0/System.Drawing.dll
%_prefix/lib/mono/2.0/System.Net.dll
%_prefix/lib/mono/2.0/System.Security.dll
%_prefix/lib/mono/2.0/System.Xml.Linq.dll
%_prefix/lib/mono/2.0/System.Xml.dll
%_prefix/lib/mono/2.0/System.dll
%_prefix/lib/mono/2.0/al.exe*
%_prefix/lib/mono/2.0/cscompmgd.dll
%_prefix/lib/mono/2.0/csharp.exe*
%_prefix/lib/mono/2.0/gacutil.exe*
%_prefix/lib/mono/2.0/gmcs.exe*
%_prefix/lib/mono/2.0/mcs.exe*
%_prefix/lib/mono/2.0/mscorlib.dll*
%_prefix/lib/mono/4.0/Commons.Xml.Relaxng.dll
%_prefix/lib/mono/4.0/CustomMarshalers.dll
%_prefix/lib/mono/4.0/I18N.West.dll
%_prefix/lib/mono/4.0/I18N.dll
%_prefix/lib/mono/4.0/ICSharpCode.SharpZipLib.dll
%_prefix/lib/mono/4.0/Microsoft.CSharp.dll
%_prefix/lib/mono/4.0/Microsoft.VisualC.dll
%_prefix/lib/mono/4.0/Mono.C5.dll
%_prefix/lib/mono/4.0/Mono.CSharp.dll
%_prefix/lib/mono/4.0/Mono.Cairo.dll
%_prefix/lib/mono/4.0/Mono.CompilerServices.SymbolWriter.dll
%_prefix/lib/mono/4.0/Mono.Management.dll
%_prefix/lib/mono/4.0/Mono.Posix.dll
%_prefix/lib/mono/4.0/Mono.Security.dll
%_prefix/lib/mono/4.0/Mono.Simd.dll
%_prefix/lib/mono/4.0/Mono.Tasklets.dll
%_prefix/lib/mono/4.0/OpenSystem.C.dll
%_prefix/lib/mono/4.0/System.Configuration.dll
%_prefix/lib/mono/4.0/System.Core.dll
%_prefix/lib/mono/4.0/System.Drawing.dll
%_prefix/lib/mono/4.0/System.Dynamic.dll
%_prefix/lib/mono/4.0/System.Net.dll
%_prefix/lib/mono/4.0/System.Numerics.dll
%_prefix/lib/mono/4.0/System.Security.dll
%_prefix/lib/mono/4.0/System.Xml.Linq.dll
%_prefix/lib/mono/4.0/System.Xml.dll
%_prefix/lib/mono/4.0/System.dll
%_prefix/lib/mono/4.0/al.exe*
%_prefix/lib/mono/4.0/certmgr.exe*
%_prefix/lib/mono/4.0/chktrust.exe*
%_prefix/lib/mono/4.0/cscompmgd.dll
%_prefix/lib/mono/4.0/csharp.exe*
%_prefix/lib/mono/4.0/dmcs.exe*
%_prefix/lib/mono/4.0/gacutil.exe*
%_prefix/lib/mono/4.0/mozroots.exe*
%_prefix/lib/mono/4.0/mscorlib.dll*
%_prefix/lib/mono/4.0/setreg.exe*
%_prefix/lib/mono/4.0/sn.exe*
%_prefix/lib/mono/compat-2.0/ICSharpCode.SharpZipLib.dll
%_prefix/lib/mono/gac/Commons.Xml.Relaxng
%_prefix/lib/mono/gac/CustomMarshalers
%_prefix/lib/mono/gac/I18N
%_prefix/lib/mono/gac/I18N.West
%_prefix/lib/mono/gac/ICSharpCode.SharpZipLib
%_prefix/lib/mono/gac/Microsoft.CSharp
%_prefix/lib/mono/gac/Microsoft.VisualC
%_prefix/lib/mono/gac/Mono.C5
%_prefix/lib/mono/gac/Mono.CSharp
%_prefix/lib/mono/gac/Mono.Cairo
%_prefix/lib/mono/gac/Mono.Cecil
%_prefix/lib/mono/gac/Mono.Cecil.Mdb
%_prefix/lib/mono/gac/Mono.CompilerServices.SymbolWriter
%_prefix/lib/mono/gac/Mono.Management
%_prefix/lib/mono/gac/Mono.Posix
%_prefix/lib/mono/gac/Mono.Security
%_prefix/lib/mono/gac/Mono.Simd
%_prefix/lib/mono/gac/Mono.Tasklets
%_prefix/lib/mono/gac/OpenSystem.C
%_prefix/lib/mono/gac/System
%_prefix/lib/mono/gac/System.Configuration
%_prefix/lib/mono/gac/System.Core
%_prefix/lib/mono/gac/System.Drawing
%_prefix/lib/mono/gac/System.Dynamic
%_prefix/lib/mono/gac/System.Net
%_prefix/lib/mono/gac/System.Numerics
%_prefix/lib/mono/gac/System.Security
%_prefix/lib/mono/gac/System.Xml
%_prefix/lib/mono/gac/System.Xml.Linq
%_prefix/lib/mono/gac/cscompmgd
%_prefix/lib/mono/mono-configuration-crypto
# Files normally in their own lib* package
%_libdir/libmono-2.0.so.1*
%if %sgen == yes
%_libdir/libmonosgen-2.0.so.0*
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%package -n mono-addon-locale-extras
License:        LGPL v2.1 only
Summary:        Extra locale information
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-locale-extras
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Extra locale information.

%files -n mono-addon-locale-extras
%defattr(-, root, root)
%_prefix/lib/mono/2.0/I18N.CJK.dll
%_prefix/lib/mono/2.0/I18N.MidEast.dll
%_prefix/lib/mono/2.0/I18N.Other.dll
%_prefix/lib/mono/2.0/I18N.Rare.dll
%_prefix/lib/mono/4.0/I18N.CJK.dll
%_prefix/lib/mono/4.0/I18N.MidEast.dll
%_prefix/lib/mono/4.0/I18N.Other.dll
%_prefix/lib/mono/4.0/I18N.Rare.dll
%_prefix/lib/mono/gac/I18N.CJK
%_prefix/lib/mono/gac/I18N.MidEast
%_prefix/lib/mono/gac/I18N.Other
%_prefix/lib/mono/gac/I18N.Rare

%package -n mono-addon-data
License:        LGPL v2.1 only
Summary:        Database connectivity for Mono
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-data
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Database connectivity for Mono.

%files -n mono-addon-data
%defattr(-, root, root)
%_bindir/sqlmetal
%_bindir/sqlsharp
%_mandir/man1/sqlsharp.1%ext_man
%_prefix/lib/mono/2.0/Mono.Data.Tds.dll
%_prefix/lib/mono/2.0/Novell.Directory.Ldap.dll
%_prefix/lib/mono/2.0/System.Data.DataSetExtensions.dll
%_prefix/lib/mono/2.0/System.Data.Linq.dll
%_prefix/lib/mono/2.0/System.Data.dll
%_prefix/lib/mono/2.0/System.DirectoryServices.dll
%_prefix/lib/mono/2.0/System.EnterpriseServices.dll
%_prefix/lib/mono/2.0/System.Runtime.Serialization.dll
%_prefix/lib/mono/2.0/System.Transactions.dll
%_prefix/lib/mono/4.0/Mono.Data.Tds.dll
%_prefix/lib/mono/4.0/Novell.Directory.Ldap.dll
%_prefix/lib/mono/4.0/System.Data.DataSetExtensions.dll
%_prefix/lib/mono/4.0/System.Data.Linq.dll
%_prefix/lib/mono/4.0/System.Data.dll
%_prefix/lib/mono/4.0/System.DirectoryServices.dll
%_prefix/lib/mono/4.0/System.EnterpriseServices.dll
%_prefix/lib/mono/4.0/System.Runtime.Serialization.dll
%_prefix/lib/mono/4.0/System.Transactions.dll
%_prefix/lib/mono/4.0/WebMatrix.Data.dll
%_prefix/lib/mono/4.0/sqlmetal.exe*
%_prefix/lib/mono/4.0/sqlsharp.exe*
%_prefix/lib/mono/gac/Mono.Data.Tds
%_prefix/lib/mono/gac/Novell.Directory.Ldap
%_prefix/lib/mono/gac/System.Data
%_prefix/lib/mono/gac/System.Data.DataSetExtensions
%_prefix/lib/mono/gac/System.Data.Linq
%_prefix/lib/mono/gac/System.DirectoryServices
%_prefix/lib/mono/gac/System.EnterpriseServices
%_prefix/lib/mono/gac/System.Runtime.Serialization
%_prefix/lib/mono/gac/System.Transactions
%_prefix/lib/mono/gac/WebMatrix.Data

%package -n mono-addon-winforms
License:        LGPL v2.1 only
Summary:        Mono's Windows Forms implementation
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-winforms
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Mono's Windows Forms implementation.

%files -n mono-addon-winforms
%defattr(-, root, root)
%_prefix/lib/mono/2.0/Accessibility.dll
%_prefix/lib/mono/2.0/Mono.WebBrowser.dll
%_prefix/lib/mono/2.0/System.Design.dll
%_prefix/lib/mono/2.0/System.Drawing.Design.dll
%_prefix/lib/mono/2.0/System.Windows.Forms.dll
%_prefix/lib/mono/4.0/Accessibility.dll
%_prefix/lib/mono/4.0/Mono.WebBrowser.dll
%_prefix/lib/mono/4.0/System.Design.dll
%_prefix/lib/mono/4.0/System.Drawing.Design.dll
%_prefix/lib/mono/4.0/System.Windows.Forms.DataVisualization.dll
%_prefix/lib/mono/4.0/System.Windows.Forms.dll
%_prefix/lib/mono/gac/Accessibility
%_prefix/lib/mono/gac/Mono.WebBrowser
%_prefix/lib/mono/gac/System.Design
%_prefix/lib/mono/gac/System.Drawing.Design
%_prefix/lib/mono/gac/System.Windows.Forms
%_prefix/lib/mono/gac/System.Windows.Forms.DataVisualization

%package -n mono-addon-ibm-data-db2
License:        LGPL v2.1 only
Summary:        Database connectivity for DB2
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-ibm-data-db2
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Database connectivity for DB2.

%files -n mono-addon-ibm-data-db2
%defattr(-, root, root)
%_prefix/lib/mono/2.0/IBM.Data.DB2.dll
%_prefix/lib/mono/4.0/IBM.Data.DB2.dll
%_prefix/lib/mono/gac/IBM.Data.DB2

%package -n mono-addon-extras
License:        LGPL v2.1 only
Summary:        Extra packages
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-extras
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Extra packages.

%files -n mono-addon-extras
%defattr(-, root, root)
%_bindir/mono-service
%_bindir/mono-service2
%_mandir/man1/mono-service.1%ext_man
%_prefix/lib/mono/2.0/Mono.Messaging.RabbitMQ.dll
%_prefix/lib/mono/2.0/Mono.Messaging.dll
%_prefix/lib/mono/2.0/RabbitMQ.Client.Apigen.exe*
%_prefix/lib/mono/2.0/RabbitMQ.Client.dll
%_prefix/lib/mono/2.0/System.Configuration.Install.dll
%_prefix/lib/mono/2.0/System.Management.dll
%_prefix/lib/mono/2.0/System.Messaging.dll
%_prefix/lib/mono/2.0/System.ServiceProcess.dll
%_prefix/lib/mono/2.0/mono-service.exe*
%_prefix/lib/mono/4.0/Mono.Messaging.RabbitMQ.dll
%_prefix/lib/mono/4.0/Mono.Messaging.dll
%_prefix/lib/mono/4.0/RabbitMQ.Client.Apigen.exe*
%_prefix/lib/mono/4.0/RabbitMQ.Client.dll
%_prefix/lib/mono/4.0/System.Configuration.Install.dll
%_prefix/lib/mono/4.0/System.Management.dll
%_prefix/lib/mono/4.0/System.Messaging.dll
%_prefix/lib/mono/4.0/System.Runtime.Caching.dll
%_prefix/lib/mono/4.0/System.ServiceProcess.dll
%_prefix/lib/mono/4.0/System.Xaml.dll
%_prefix/lib/mono/4.0/installutil.exe*
%_prefix/lib/mono/4.0/mono-service.exe*
%_prefix/lib/mono/gac/Mono.Messaging
%_prefix/lib/mono/gac/Mono.Messaging.RabbitMQ
%_prefix/lib/mono/gac/RabbitMQ.Client
%_prefix/lib/mono/gac/System.Configuration.Install
%_prefix/lib/mono/gac/System.Management
%_prefix/lib/mono/gac/System.Messaging
%_prefix/lib/mono/gac/System.Runtime.Caching
%_prefix/lib/mono/gac/System.ServiceProcess
%_prefix/lib/mono/gac/System.Xaml
%_prefix/lib/mono/gac/mono-service

%package -n mono-addon-data-sqlite
License:        LGPL v2.1 only
Summary:        Database connectivity for Mono
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release
Requires:       mono-addon-data == %version-%release

%description -n mono-addon-data-sqlite
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Database connectivity for Mono.

%files -n mono-addon-data-sqlite
%defattr(-, root, root)
%_prefix/lib/mono/2.0/Mono.Data.Sqlite.dll
%_prefix/lib/mono/4.0/Mono.Data.Sqlite.dll
%_prefix/lib/mono/gac/Mono.Data.Sqlite

%package -n mono-addon-wcf
License:        MIT License (or similar) ; Ms-Pl
Summary:        Mono implementation of WCF, Windows Communication Foundation
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-wcf
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Mono implementation of WCF, Windows Communication Foundation

%files -n mono-addon-wcf
%defattr(-, root, root)
%_bindir/svcutil
%_libdir/pkgconfig/wcf.pc
%_prefix/lib/mono/2.0/System.Data.Services.dll
%_prefix/lib/mono/2.0/System.IdentityModel.Selectors.dll
%_prefix/lib/mono/2.0/System.IdentityModel.dll
%_prefix/lib/mono/2.0/System.ServiceModel.Web.dll
%_prefix/lib/mono/2.0/System.ServiceModel.dll
%_prefix/lib/mono/4.0/System.Data.Services.dll
%_prefix/lib/mono/4.0/System.IdentityModel.Selectors.dll
%_prefix/lib/mono/4.0/System.IdentityModel.dll
%_prefix/lib/mono/4.0/System.Runtime.DurableInstancing.dll
%_prefix/lib/mono/4.0/System.ServiceModel.Discovery.dll
%_prefix/lib/mono/4.0/System.ServiceModel.Routing.dll
%_prefix/lib/mono/4.0/System.ServiceModel.Web.dll
%_prefix/lib/mono/4.0/System.ServiceModel.dll
%_prefix/lib/mono/4.0/svcutil.exe*
%_prefix/lib/mono/gac/System.Data.Services
%_prefix/lib/mono/gac/System.IdentityModel
%_prefix/lib/mono/gac/System.IdentityModel.Selectors
%_prefix/lib/mono/gac/System.Runtime.DurableInstancing
%_prefix/lib/mono/gac/System.ServiceModel
%_prefix/lib/mono/gac/System.ServiceModel.Discovery
%_prefix/lib/mono/gac/System.ServiceModel.Routing
%_prefix/lib/mono/gac/System.ServiceModel.Web

%package -n mono-addon-winfxcore
License:        MIT License (or similar) ; Ms-Pl
Summary:        Mono implementation of core WinFX APIs
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-winfxcore
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Mono implementation of core WinFX APIs

%files -n mono-addon-winfxcore
%defattr(-, root, root)
%_prefix/lib/mono/2.0/System.Data.Services.Client.dll*
%_prefix/lib/mono/2.0/WindowsBase.dll*
%_prefix/lib/mono/4.0/System.Data.Services.Client.dll*
%_prefix/lib/mono/4.0/WindowsBase.dll*
%_prefix/lib/mono/gac/System.Data.Services.Client
%_prefix/lib/mono/gac/WindowsBase

%package -n mono-addon-web
License:        MIT License (or similar) ; Ms-Pl
Summary:        Mono implementation of ASP.NET, Remoting and Web Services
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-web
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Mono implementation of ASP.NET, Remoting and Web Services.

%files -n mono-addon-web
%defattr(-, root, root)
%config %_sysconfdir/mono/2.0/Browsers
%config %_sysconfdir/mono/2.0/DefaultWsdlHelpGenerator.aspx
%config %_sysconfdir/mono/2.0/web.config
%config %_sysconfdir/mono/4.0/DefaultWsdlHelpGenerator.aspx
%config %_sysconfdir/mono/4.0/web.config
%config %_sysconfdir/mono/browscap.ini
%config %_sysconfdir/mono/mconfig/config.xml
%dir %_sysconfdir/mono/mconfig
%_bindir/disco
%_bindir/mconfig
%_bindir/soapsuds
%_bindir/wsdl
%_bindir/wsdl2
%_bindir/xsd
%_libdir/pkgconfig/mono.web.pc
%_mandir/man1/disco.1%ext_man
%_mandir/man1/mconfig.1%ext_man
%_mandir/man1/soapsuds.1%ext_man
%_mandir/man1/wsdl.1%ext_man
%_mandir/man1/xsd.1%ext_man
%_prefix/lib/mono/2.0/Mono.Http.dll
%_prefix/lib/mono/2.0/Mono.Web.dll
%_prefix/lib/mono/2.0/System.ComponentModel.DataAnnotations.dll
%_prefix/lib/mono/2.0/System.Runtime.Remoting.dll
%_prefix/lib/mono/2.0/System.Runtime.Serialization.Formatters.Soap.dll
%_prefix/lib/mono/2.0/System.Web.Abstractions.dll
%_prefix/lib/mono/2.0/System.Web.Routing.dll
%_prefix/lib/mono/2.0/System.Web.Services.dll
%_prefix/lib/mono/2.0/System.Web.dll
%_prefix/lib/mono/2.0/wsdl.exe*
%_prefix/lib/mono/2.0/xsd.exe*
%_prefix/lib/mono/4.0/Microsoft.Web.Infrastructure.dll
%_prefix/lib/mono/4.0/Mono.Http.dll
%_prefix/lib/mono/4.0/Mono.Web.dll
%_prefix/lib/mono/4.0/System.ComponentModel.Composition.dll
%_prefix/lib/mono/4.0/System.ComponentModel.DataAnnotations.dll
%_prefix/lib/mono/4.0/System.Runtime.Remoting.dll
%_prefix/lib/mono/4.0/System.Runtime.Serialization.Formatters.Soap.dll
%_prefix/lib/mono/4.0/System.Web.Abstractions.dll
%_prefix/lib/mono/4.0/System.Web.ApplicationServices.dll
%_prefix/lib/mono/4.0/System.Web.Routing.dll
%_prefix/lib/mono/4.0/System.Web.Services.dll
%_prefix/lib/mono/4.0/System.Web.dll
%_prefix/lib/mono/4.0/disco.exe*
%_prefix/lib/mono/4.0/mconfig.exe*
%_prefix/lib/mono/4.0/soapsuds.exe*
%_prefix/lib/mono/4.0/wsdl.exe*
%_prefix/lib/mono/4.0/xsd.exe*
%_prefix/lib/mono/gac/Microsoft.Web.Infrastructure
%_prefix/lib/mono/gac/Mono.Http
%_prefix/lib/mono/gac/Mono.Web
%_prefix/lib/mono/gac/System.ComponentModel.Composition
%_prefix/lib/mono/gac/System.ComponentModel.DataAnnotations
%_prefix/lib/mono/gac/System.Runtime.Remoting
%_prefix/lib/mono/gac/System.Runtime.Serialization.Formatters.Soap
%_prefix/lib/mono/gac/System.Web
%_prefix/lib/mono/gac/System.Web.Abstractions
%_prefix/lib/mono/gac/System.Web.ApplicationServices
%_prefix/lib/mono/gac/System.Web.Routing
%_prefix/lib/mono/gac/System.Web.Services

%package -n mono-addon-mvc
License:        MIT License (or similar) ; Ms-Pl
Summary:        Mono implementation of ASP.NET MVC
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-mvc
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Mono implementation of ASP.NET MVC.

%files -n mono-addon-mvc
%defattr(-, root, root)
%_libdir/pkgconfig/system.web.extensions.design_1.0.pc
%_libdir/pkgconfig/system.web.extensions_1.0.pc
%_libdir/pkgconfig/system.web.mvc.pc
%_libdir/pkgconfig/system.web.mvc2.pc
%_prefix/lib/mono/2.0/System.Web.DynamicData.dll
%_prefix/lib/mono/2.0/System.Web.Extensions.Design.dll
%_prefix/lib/mono/2.0/System.Web.Extensions.dll
%_prefix/lib/mono/2.0/System.Web.Mvc.dll
%_prefix/lib/mono/4.0/System.Web.DynamicData.dll
%_prefix/lib/mono/4.0/System.Web.Extensions.Design.dll
%_prefix/lib/mono/4.0/System.Web.Extensions.dll
%_prefix/lib/mono/compat-2.0/System.Web.Extensions.Design.dll
%_prefix/lib/mono/compat-2.0/System.Web.Extensions.dll
%_prefix/lib/mono/compat-2.0/System.Web.Mvc.dll
%_prefix/lib/mono/gac/System.Web.DynamicData
%_prefix/lib/mono/gac/System.Web.Extensions
%_prefix/lib/mono/gac/System.Web.Extensions.Design
%_prefix/lib/mono/gac/System.Web.Mvc

%package -n mono-addon-data-oracle
License:        LGPL v2.1 only
Summary:        Database connectivity for Mono
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release
Requires:       mono-addon-data == %version-%release

%description -n mono-addon-data-oracle
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Database connectivity for Mono.

%files -n mono-addon-data-oracle
%defattr(-, root, root)
%_prefix/lib/mono/2.0/System.Data.OracleClient.dll
%_prefix/lib/mono/4.0/System.Data.OracleClient.dll
%_prefix/lib/mono/gac/System.Data.OracleClient

%package -n mono-addon-data-postgresql
License:        LGPL v2.1 only
Summary:        Database connectivity for Mono
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release
Requires:       mono-addon-data == %version-%release

%description -n mono-addon-data-postgresql
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. The project will implement various
technologies that have been submitted to the ECMA for standardization.

Database connectivity for Mono.

%files -n mono-addon-data-postgresql
%defattr(-, root, root)
%_prefix/lib/mono/2.0/Npgsql.dll
%_prefix/lib/mono/4.0/Npgsql.dll
%_prefix/lib/mono/gac/Npgsql

%package -n mono-addon-nunit
License:        LGPL v2.1 only
Summary:        NUnit Testing Framework
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release

%description -n mono-addon-nunit
NUnit is a unit-testing framework for all .Net languages.  Initially
ported from JUnit, the current release, version 2.2,  is the fourth
major release of this  Unit based unit testing tool for Microsoft .NET.
It is written entirely in C# and  has been completely redesigned to
take advantage of many .NET language		 features, for example
custom attributes and other reflection related capabilities. NUnit
brings xUnit to all .NET languages.

%files -n mono-addon-nunit
%defattr(-, root, root)
%_libdir/pkgconfig/mono-nunit.pc
%_prefix/bin/nunit-console
%_prefix/bin/nunit-console2
%_prefix/lib/mono/2.0/nunit-console-runner.dll
%_prefix/lib/mono/2.0/nunit-console.exe*
%_prefix/lib/mono/2.0/nunit.core.dll
%_prefix/lib/mono/2.0/nunit.core.extensions.dll
%_prefix/lib/mono/2.0/nunit.core.interfaces.dll
%_prefix/lib/mono/2.0/nunit.framework.dll
%_prefix/lib/mono/2.0/nunit.framework.extensions.dll
%_prefix/lib/mono/2.0/nunit.mocks.dll
%_prefix/lib/mono/2.0/nunit.util.dll
%_prefix/lib/mono/4.0/nunit-console-runner.dll
%_prefix/lib/mono/4.0/nunit-console.exe*
%_prefix/lib/mono/4.0/nunit.core.dll
%_prefix/lib/mono/4.0/nunit.core.extensions.dll
%_prefix/lib/mono/4.0/nunit.core.interfaces.dll
%_prefix/lib/mono/4.0/nunit.framework.dll
%_prefix/lib/mono/4.0/nunit.framework.extensions.dll
%_prefix/lib/mono/4.0/nunit.mocks.dll
%_prefix/lib/mono/4.0/nunit.util.dll
%_prefix/lib/mono/gac/nunit-console-runner
%_prefix/lib/mono/gac/nunit.core
%_prefix/lib/mono/gac/nunit.core.extensions
%_prefix/lib/mono/gac/nunit.core.interfaces
%_prefix/lib/mono/gac/nunit.framework
%_prefix/lib/mono/gac/nunit.framework.extensions
%_prefix/lib/mono/gac/nunit.mocks
%_prefix/lib/mono/gac/nunit.util

%package -n mono-addon-devel
License:        LGPL v2.1 only
Summary:        Mono development tools
Group:          Development/Languages/Mono
Requires:       mono-addon-core == %version-%release
Requires:       mono-addon-libgdiplus0
Requires:       pkgconfig
# Required because they are referenced by .pc files
Requires:       mono-addon-data == %version-%release
Requires:       mono-addon-data-oracle == %version-%release
Requires:       mono-addon-extras == %version-%release
Requires:       mono-addon-web == %version-%release
Requires:       mono-addon-winforms == %version-%release

%description -n mono-addon-devel
The Mono Project is an open development initiative that is working to
develop an open source, Unix version of the .NET development platform.
Its objective is to enable Unix developers to build and deploy
cross-platform .NET applications. This package contains compilers and
other tools needed to develop .NET applications.

Mono development tools.

%files -n mono-addon-devel
%defattr(-, root, root)
%_bindir/caspol
%_bindir/ccrewrite
%_bindir/cert2spc
%_bindir/dtd2rng
%_bindir/dtd2xsd
%_bindir/genxs
%_bindir/httpcfg
%_bindir/ilasm
%_bindir/installvst
%_bindir/lc
%_bindir/macpack
%_bindir/makecert
%_bindir/mkbundle
%_bindir/mono-api-info
%_bindir/mono-cil-strip
%_bindir/mono-find-provides
%_bindir/mono-find-requires
%_bindir/mono-heapviz
%_bindir/mono-shlib-cop
%_bindir/mono-xmltool
%_bindir/monodis
%_bindir/monograph
%_bindir/monolinker
%_bindir/monop
%_bindir/monop2
%_bindir/mprof-report
%_bindir/pdb2mdb
%_bindir/pedump
%_bindir/permview
%_bindir/prj2make
%_bindir/resgen
%_bindir/resgen2
%_bindir/secutil
%_bindir/sgen
%_bindir/signcode
%_bindir/xbuild
%dir %_datadir/mono-2.0
%dir %_datadir/mono-2.0/mono
%dir %_datadir/mono-2.0/mono/cil
%_datadir/mono-2.0/mono/cil/cil-opcodes.xml
%_libdir/libmono-profiler-*.*
%_libdir/pkgconfig/cecil.pc
%_libdir/pkgconfig/dotnet.pc
%_libdir/pkgconfig/dotnet35.pc
%_libdir/pkgconfig/mono-cairo.pc
%_libdir/pkgconfig/mono-lineeditor.pc
%_libdir/pkgconfig/mono-options.pc
%_libdir/pkgconfig/mono.pc
%_mandir/man1/al.1%ext_man
%_mandir/man1/ccrewrite.1%ext_man
%_mandir/man1/cert2spc.1%ext_man
%_mandir/man1/dtd2xsd.1%ext_man
%_mandir/man1/genxs.1%ext_man
%_mandir/man1/httpcfg.1%ext_man
%_mandir/man1/ilasm.1%ext_man
%_mandir/man1/lc.1%ext_man
%_mandir/man1/macpack.1%ext_man
%_mandir/man1/makecert.1%ext_man
%_mandir/man1/mkbundle.1%ext_man
%_mandir/man1/mono-api-info.1%ext_man
%_mandir/man1/mono-cil-strip.1%ext_man
%_mandir/man1/mono-shlib-cop.1%ext_man
%_mandir/man1/mono-xmltool.1%ext_man
%_mandir/man1/monodis.1%ext_man
%_mandir/man1/monolinker.1%ext_man
%_mandir/man1/monop.1%ext_man
%_mandir/man1/mprof-report.1%ext_man
%_mandir/man1/pdb2mdb.1%ext_man
%_mandir/man1/permview.1%ext_man
%_mandir/man1/prj2make.1%ext_man
%_mandir/man1/resgen.1%ext_man
%_mandir/man1/secutil.1%ext_man
%_mandir/man1/sgen.1%ext_man
%_mandir/man1/signcode.1%ext_man
%_mandir/man1/xbuild.1%ext_man
%_prefix/lib/mono-source-libs
%_prefix/lib/mono/2.0/MSBuild
%_prefix/lib/mono/2.0/Microsoft.Build.Engine.dll
%_prefix/lib/mono/2.0/Microsoft.Build.Framework.dll
%_prefix/lib/mono/2.0/Microsoft.Build.Tasks.dll
%_prefix/lib/mono/2.0/Microsoft.Build.Utilities.dll
%_prefix/lib/mono/2.0/Microsoft.Build.xsd
%_prefix/lib/mono/2.0/Microsoft.CSharp.targets
%_prefix/lib/mono/2.0/Microsoft.Common.targets
%_prefix/lib/mono/2.0/Microsoft.Common.tasks
%_prefix/lib/mono/2.0/Microsoft.VisualBasic.targets
%_prefix/lib/mono/2.0/Mono.Debugger.Soft.dll
%_prefix/lib/mono/2.0/PEAPI.dll
%_prefix/lib/mono/2.0/genxs.exe*
%_prefix/lib/mono/2.0/ilasm.exe*
%_prefix/lib/mono/2.0/mkbundle.exe*
%_prefix/lib/mono/2.0/monolinker.*
%_prefix/lib/mono/2.0/monop.exe*
%_prefix/lib/mono/2.0/resgen.exe*
%_prefix/lib/mono/2.0/xbuild.exe*
%_prefix/lib/mono/2.0/xbuild.rsp
%_prefix/lib/mono/3.5/MSBuild
%_prefix/lib/mono/3.5/Microsoft.Build.Engine.dll
%_prefix/lib/mono/3.5/Microsoft.Build.Framework.dll
%_prefix/lib/mono/3.5/Microsoft.Build.Tasks.v3.5.dll
%_prefix/lib/mono/3.5/Microsoft.Build.Utilities.v3.5.dll
%_prefix/lib/mono/3.5/Microsoft.Build.xsd
%_prefix/lib/mono/3.5/Microsoft.CSharp.targets
%_prefix/lib/mono/3.5/Microsoft.Common.targets
%_prefix/lib/mono/3.5/Microsoft.Common.tasks
%_prefix/lib/mono/3.5/Microsoft.VisualBasic.targets
%_prefix/lib/mono/3.5/xbuild.exe*
%_prefix/lib/mono/3.5/xbuild.rsp
%_prefix/lib/mono/4.0/MSBuild
%_prefix/lib/mono/4.0/Microsoft.Build.Engine.dll
%_prefix/lib/mono/4.0/Microsoft.Build.Framework.dll
%_prefix/lib/mono/4.0/Microsoft.Build.Tasks.v4.0.dll
%_prefix/lib/mono/4.0/Microsoft.Build.Utilities.v4.0.dll
%_prefix/lib/mono/4.0/Microsoft.Build.xsd
%_prefix/lib/mono/4.0/Microsoft.CSharp.targets
%_prefix/lib/mono/4.0/Microsoft.Common.targets
%_prefix/lib/mono/4.0/Microsoft.Common.tasks
%_prefix/lib/mono/4.0/Microsoft.VisualBasic.targets
%_prefix/lib/mono/4.0/Mono.CodeContracts.dll
%_prefix/lib/mono/4.0/Mono.Debugger.Soft.dll
%_prefix/lib/mono/4.0/PEAPI.dll
%_prefix/lib/mono/4.0/caspol.exe*
%_prefix/lib/mono/4.0/ccrewrite.exe*
%_prefix/lib/mono/4.0/cert2spc.exe*
%_prefix/lib/mono/4.0/dtd2rng.exe*
%_prefix/lib/mono/4.0/dtd2xsd.exe*
%_prefix/lib/mono/4.0/genxs.exe*
%_prefix/lib/mono/4.0/httpcfg.exe*
%_prefix/lib/mono/4.0/ictool.exe*
%_prefix/lib/mono/4.0/ilasm.exe*
%_prefix/lib/mono/4.0/installvst.exe*
%_prefix/lib/mono/4.0/lc.exe*
%_prefix/lib/mono/4.0/macpack.exe*
%_prefix/lib/mono/4.0/makecert.exe*
%_prefix/lib/mono/4.0/mkbundle.exe*
%_prefix/lib/mono/4.0/mono-api-info.exe*
%_prefix/lib/mono/4.0/mono-cil-strip.exe*
%_prefix/lib/mono/4.0/mono-shlib-cop.exe*
%_prefix/lib/mono/4.0/mono-xmltool.exe*
%_prefix/lib/mono/4.0/monolinker.*
%_prefix/lib/mono/4.0/monop.exe*
%_prefix/lib/mono/4.0/pdb2mdb.exe*
%_prefix/lib/mono/4.0/permview.exe*
%_prefix/lib/mono/4.0/resgen.exe*
%_prefix/lib/mono/4.0/secutil.exe*
%_prefix/lib/mono/4.0/sgen.exe*
%_prefix/lib/mono/4.0/signcode.exe*
%_prefix/lib/mono/4.0/xbuild.exe*
%_prefix/lib/mono/4.0/xbuild.rsp
%_prefix/lib/mono/gac/Microsoft.Build.Engine
%_prefix/lib/mono/gac/Microsoft.Build.Framework
%_prefix/lib/mono/gac/Microsoft.Build.Tasks
%_prefix/lib/mono/gac/Microsoft.Build.Tasks.v3.5
%_prefix/lib/mono/gac/Microsoft.Build.Tasks.v4.0
%_prefix/lib/mono/gac/Microsoft.Build.Utilities
%_prefix/lib/mono/gac/Microsoft.Build.Utilities.v3.5
%_prefix/lib/mono/gac/Microsoft.Build.Utilities.v4.0
%_prefix/lib/mono/gac/Mono.CodeContracts
%_prefix/lib/mono/gac/Mono.Debugger.Soft
%_prefix/lib/mono/gac/PEAPI
%_prefix/lib/mono/xbuild
%_prefix/lib/mono/xbuild-frameworks
# Files normally in -devel packages
%_bindir/mono-gdb.py
%_includedir/mono-2.0
%_libdir/libmono-2.0.a
%_libdir/libmono-2.0.so
%_libdir/pkgconfig/mono-2.pc
%if %sgen == yes
%_bindir/mono-sgen-gdb.py
%_libdir/libmonosgen-2.0.a
%_libdir/libmonosgen-2.0.so
%_libdir/pkgconfig/monosgen-2.pc
%endif

%post -n mono-addon-devel -p /sbin/ldconfig

%postun -n mono-addon-devel -p /sbin/ldconfig

%package -n monodoc-addon-core
License:        LGPL v2.1 only
Summary:        Monodoc - Documentation tools for C# code
Group:          Development/Tools/Other
Requires:       mono-addon-core == %version-%release
# Added to uncompress and compare documentation used by build-compare
Requires:       unzip

%description -n monodoc-addon-core
Monodoc-core contains documentation tools for C#.

%files -n monodoc-addon-core
%defattr(-, root, root)
%_bindir/mdassembler
%_bindir/mdoc
%_bindir/mdoc-assemble
%_bindir/mdoc-export-html
%_bindir/mdoc-export-msxdoc
%_bindir/mdoc-update
%_bindir/mdoc-validate
%_bindir/mdvalidater
%_bindir/mod
%_bindir/monodocer
%_bindir/monodocs2html
%_bindir/monodocs2slashdoc
%_libdir/pkgconfig/monodoc.pc
%_mandir/man1/mdassembler.1%ext_man
%_mandir/man1/mdoc-assemble.1%ext_man
%_mandir/man1/mdoc-export-html.1%ext_man
%_mandir/man1/mdoc-export-msxdoc.1%ext_man
%_mandir/man1/mdoc-update.1%ext_man
%_mandir/man1/mdoc-validate.1%ext_man
%_mandir/man1/mdoc.1%ext_man
%_mandir/man1/mdvalidater.1%ext_man
%_mandir/man1/monodocer.1%ext_man
%_mandir/man1/monodocs2html.1%ext_man
%_mandir/man5/mdoc.5%ext_man
%_prefix/lib/mono/2.0/mdoc.exe*
%_prefix/lib/mono/4.0/mod.exe*
%_prefix/lib/mono/gac/monodoc
%_prefix/lib/mono/monodoc
%_prefix/lib/monodoc

%changelog
* Wed Feb 23 2011 AJorgensen@novell.com
- Update to 2.10.1
  * http://go-mono.com/archive/2.10.1
* Tue Feb  1 2011 ajorgensen@novell.com
- Update to 2.10
  * http://go-mono.com/archive/2.10
* Tue Sep 15 2009 ajorgensen@novell.com
- Patch for bnc#538588
* Tue Aug 11 2009 ajorgensen@novell.com
- Update to 2.4.2.3
  * http://www.mono-project.com/Release_Notes_Mono_2.4.2.3
* Wed Jul 15 2009 ajorgensen@novell.com
- Patch for CVE-2009-0217, bnc#521184
* Fri Apr 17 2009 meissner@suse.de
- ppc: increase stacksize in collection.c to make it build on newer
  PowerPC kernels.
* Fri Mar 13 2009 ajorgensen@novell.com
- Update to 2.4 RC3
* Tue Mar 10 2009 ajorgensen@suse.de
- Update to 2.4 RC2
- Move installutil.exe to mono-extras (should break dep on -extras)
- Add mono.web.pc
* Tue Mar  3 2009 ajorgensen@novell.com
- Remove mono-addon-complete (meta-package)
* Mon Feb 23 2009 ajorgensen@novell.com
- Update to 2.4 (RC1)
* Tue Feb 17 2009 ajorgensen@suse.de
- Move Mono.Cecil from mono-devel to mono-core
* Sat Feb 14 2009 ajorgensen@suse.de
- Add a wrapper script to mono so that it will load the right
  native libraries (may be temporary if our engineers come up with
  something better before release)
* Sat Feb 14 2009 ajorgensen@novell.com
- Update to 2.4-preview3
* Mon Feb  2 2009 ajorgensen@suse.de
- Fixed find-provides / find-requires scripts for addon
* Mon Feb  2 2009 ajorgensen@suse.de
- Remove obsoleted patch
* Fri Jan 30 2009 ajorgensen@novell.com
- Update to 2.4 (preview 2)
* Mon Jan 26 2009 ajorgensen@novell.com
- Patch for emit_sig_cookie compile problem
* Fri Jan 23 2009 ajorgensen@novell.com
- Update to 2.4 (preview 1)
* Tue Dec 16 2008 ajorgensen@suse.de
- Mono ASP.NET Add-On 2.0
