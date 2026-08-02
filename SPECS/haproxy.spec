%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy

# This package targets RHEL 8 and 9 (and rebuilds such as Rocky/Alma) only.
# Fail early and clearly rather than producing a subtly wrong package.
%if !(0%{?el8} || 0%{?el9})
%{error:haproxy: unsupported build target (dist=%{?dist}). RHEL 8 or 9 required.}
%endif

%global _hardened_build 1

Summary: HA-Proxy reverse proxy for high availability environments
Name: haproxy
Version: %{version}
Release: %{release}%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/%{mainversion}/src/%{name}-%{version}.tar.gz
Source1: %{name}.cfg
Source2: %{name}.service
Source3: %{name}.logrotate
Source4: %{name}.syslog%{?dist}
Source5: halog.1

# 바로 쓸 수 있는 설정 예제. %%prep 에서 recipes/ 로 모아 %%doc 로 패키징합니다.
Source10: README.txt
Source11: 01-web-http.cfg
Source12: 02-https.cfg
Source13: 03-routing.cfg
Source14: 04-sticky-session.cfg
Source15: 05-basic-auth.cfg
Source16: 06-mysql.cfg
Source17: 07-postgresql.cfg
Source18: 08-redis.cfg
Source19: 09-tcp.cfg
Source20: 10-rate-limit.cfg
Source21: 11-maintenance.cfg
Source22: 12-dynamic-exclusion.cfg

BuildRoot: %{_tmppath}/%{name}-%{version}-root

BuildRequires: pcre-devel
BuildRequires: zlib-devel
BuildRequires: make
BuildRequires: gcc openssl-devel
BuildRequires: openssl-devel

Requires(pre):      shadow-utils
Requires:           rsyslog


BuildRequires:      systemd-units
BuildRequires:      systemd-devel
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

Ready-to-use configuration recipes are installed under
%{_docdir}/%{name}/recipes.

https://github.com/DataDynamics-OSS/haproxy3-rpm-builder

%prep
%setup -q

# Ready-to-use config recipes, shipped as documentation. They are collected
# here rather than installed straight into %%{_docdir}: the %%doc directive
# wipes and recreates that directory, which would drop anything %%install put
# there first.
%{__mkdir_p} recipes
for f in %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13} %{SOURCE14} \
         %{SOURCE15} %{SOURCE16} %{SOURCE17} %{SOURCE18} %{SOURCE19} \
         %{SOURCE20} %{SOURCE21} %{SOURCE22}; do
    %{__install} -c -m 644 "$f" recipes/
done

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif

RPM_BUILD_NCPUS="`/usr/bin/nproc 2>/dev/null || /usr/bin/getconf _NPROCESSORS_ONLN`";

# Default opts
systemd_opts=
pcre_opts="USE_PCRE=1"
USE_TFO=
USE_NS=

systemd_opts="USE_SYSTEMD=1"
pcre_opts="USE_PCRE=1 USE_PCRE_JIT=1"

USE_TFO=1
USE_NS=1

%if 0%{_use_lua}
SET_LUA="USE_LUA=1"
%endif

%if 0%{_use_prometheus}
SET_PROMETHEUS="USE_PROMEX=1"
%endif

%{__make} -j$RPM_BUILD_NCPUS %{?_smp_mflags} CPU="generic" TARGET="linux-glibc" ${systemd_opts} ${pcre_opts} USE_OPENSSL=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 USE_THREAD=1 USE_TFO=${USE_TFO} USE_NS=${USE_NS} ${SET_LUA} ${SET_PROMETHEUS} ADDLIB="%{__global_ldflags}"

%{__make} admin/halog/halog OPTIMIZE="%{optflags} %{__global_ldflags}"

pushd admin/iprange
%{__make} iprange OPTIMIZE="%{optflags} %{__global_ldflags}"
popd

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_bindir}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/errors
%{__install} -d %{buildroot}%{_mandir}/man1/
%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d %{buildroot}%{_sysconfdir}/rsyslog.d
%{__install} -d %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -d %{buildroot}%{haproxy_home}

%{__install} -s %{name} %{buildroot}%{_sbindir}/


%{__install} -c -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/haproxy.cfg
%{__install} -c -m 644 examples/errorfiles/*.http %{buildroot}%{_sysconfdir}/%{name}/errors/
%{__install} -c -m 644 doc/%{name}.1 %{buildroot}%{_mandir}/man1/
%{__install} -c -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{__install} -c -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__install} -p -m 0755 ./admin/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./admin/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1


%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%pre
getent group %{haproxy_group} >/dev/null || \
       groupadd -g 188 -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
       useradd -u 188 -r -g %{haproxy_group} -d %{haproxy_home} \
       -s /sbin/nologin -c "%{name}" %{haproxy_user}
exit 0

%post
%systemd_post %{name}.service
systemctl reload-or-try-restart rsyslog.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service
systemctl reload-or-try-restart rsyslog.service


%files
%defattr(-,root,root)
%doc CHANGELOG examples/*.cfg doc/configuration.txt doc/intro.txt doc/management.txt doc/proxy-protocol.txt
%doc recipes
    %license LICENSE
%doc %{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/errors
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0755,root,root) %{_sbindir}/%{name}
%dir %{_localstatedir}/log/%{name}
%dir %attr(0755,%{haproxy_user},%{haproxy_group}) %{haproxy_home}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{_bindir}/halog
%{_bindir}/iprange


%attr(-,root,root) %{_unitdir}/%{name}.service
