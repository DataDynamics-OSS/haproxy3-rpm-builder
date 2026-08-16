==============================================================================
 HAProxy 설정 예제 모음
==============================================================================

이 디렉터리에는 실무에서 자주 쓰는 설정을 용도별로 나눠 담았습니다.
필요한 것만 골라서 /etc/haproxy/haproxy.cfg 끝에 붙여 넣고, IP 주소와 포트만
환경에 맞게 바꾸면 됩니다.

각 파일 맨 위 주석에 무엇을 하는 설정인지, 무엇을 먼저 준비해야 하는지,
어떤 값을 바꿔야 하는지가 적혀 있습니다. 먼저 읽어 보세요.

------------------------------------------------------------------------------
 두 벌이 들어 있습니다
------------------------------------------------------------------------------

같은 주제를 다루는 예제 모음이 두 벌 있습니다. 성격이 달라 둘 다 남겼습니다.
아무거나 하나를 골라 쓰면 되고, 섞어 쓸 필요는 없습니다.

  숫자로 시작하는 파일    NN-....cfg
      주제를 잘게 나눈 세트입니다. 한 파일이 한 가지만 다루므로 필요한 것만
      집어 오기 쉽고, 아래 check-example.sh 로 문법 검사를 할 수 있습니다.
      외부 스크립트 실행(external-check) 예제는 이쪽에만 있습니다.

  recipe- 로 시작하는 파일  recipe-NN-....cfg
      주제를 굵직하게 묶은 세트입니다. 한 파일에 관련 설정이 함께 들어 있어
      처음부터 끝까지 읽어 내려가며 익히기 좋습니다. HTTP 기본 인증과 맵 파일
      동적 차단은 이쪽에만 있습니다.

------------------------------------------------------------------------------
 파일 목록 — 잘게 나눈 세트
------------------------------------------------------------------------------

  00-base.cfg               문법 검사용 global/defaults 뼈대 (붙여 넣는 예제 아님)
  15-external-check.global  15번 예제 전용 뼈대 (붙여 넣는 예제 아님)

  01-web-http-lb.cfg        웹 서버 부하 분산 (HTTP) — 가장 기본
  02-real-client-ip.cfg     백엔드에 진짜 접속자 IP 알려주기 (X-Forwarded-For)
  03-https-offload.cfg      HTTPS 처리 (SSL 종료) + HTTP→HTTPS 리다이렉트
  04-http2.cfg              HTTP/2 사용하기 (ALPN)
  05-routing-acl.cfg        경로·도메인별로 다른 서버에 보내기 (ACL)
  06-sticky-session.cfg     세션 고정 (쿠키 방식 / IP 방식)
  07-mysql.cfg              MySQL·MariaDB 부하 분산
  08-mysql-rw-split.cfg     MySQL·MariaDB 쓰기·읽기 포트 분리
  09-postgresql.cfg         PostgreSQL 부하 분산
  10-redis.cfg              Redis 마스터 자동 선택
  11-tcp-passthrough.cfg    일반 TCP 서비스 중계 (SMTP 등)
  12-rate-limit.cfg         접속 제한과 속도 제한
  13-maintenance.cfg        서버 점검(maintenance) 처리
  14-agent-check.cfg        외부 에이전트로 상태·가중치 동적 제어 (권장)
  15-external-check.cfg     외부 스크립트를 실행해 헬스체크 (chroot 꺼야 함)

  check-example.sh          예제 하나를 문법 검사해 주는 도우미 스크립트

------------------------------------------------------------------------------
 파일 목록 — 굵직하게 묶은 세트
------------------------------------------------------------------------------

  recipe-01-web-http.cfg          웹 서버 부하 분산 (HTTP), 헬스체크 조정
  recipe-02-https.cfg             HTTPS 처리(SSL 종료), HTTP→HTTPS 전환, HTTP/2
  recipe-03-routing.cfg           경로·도메인별 라우팅 (ACL)
  recipe-04-sticky-session.cfg    세션 고정 (쿠키 / 접속자 IP)
  recipe-05-basic-auth.cfg        HTTP 기본 인증          <-- 이쪽에만 있음
  recipe-06-mysql.cfg             MySQL/MariaDB (읽기·쓰기 분리 포함)
  recipe-07-postgresql.cfg        PostgreSQL
  recipe-08-redis.cfg             Redis (마스터 자동 판별)
  recipe-09-tcp.cfg               일반 TCP 서비스 중계
  recipe-10-rate-limit.cfg        접속 제한과 속도 제한
  recipe-11-maintenance.cfg       서버 점검 처리
  recipe-12-dynamic-exclusion.cfg 외부 정보로 서버를 동적으로 제외
                                  (agent-check / Runtime API / 맵 파일)
                                  맵 파일 동적 차단은 이쪽에만 있음

------------------------------------------------------------------------------
 예제를 적용하는 공통 절차
------------------------------------------------------------------------------

어떤 예제든 방법은 똑같습니다. 이 세 단계를 습관으로 만드세요.

  # 1. 백업
  sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak

  # 2. 예제를 파일 끝에 붙이고 IP·포트 수정
  sudo sh -c 'cat /usr/share/haproxy/examples/01-web-http-lb.cfg >> /etc/haproxy/haproxy.cfg'
  sudo vi /etc/haproxy/haproxy.cfg

  # 3. 문법 검사가 통과할 때만 반영
  sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy

3단계에서 && 로 이어 둔 것이 중요합니다. 문법 검사가 실패하면 리로드가 아예
실행되지 않으므로, 잘못된 설정이 서비스에 반영되는 사고를 막아 줍니다.

------------------------------------------------------------------------------
 붙여 넣기 전에 예제만 따로 검사하기
------------------------------------------------------------------------------

예제 파일에는 frontend/backend/listen 블록만 들어 있어 그대로는 검사할 수
없습니다. 00-base.cfg 를 앞에 붙여 주면 됩니다. HAProxy는 -f 를 여러 번 쓰면
파일을 순서대로 이어 붙여 읽습니다.

  haproxy -c -f /usr/share/haproxy/examples/00-base.cfg \
             -f /usr/share/haproxy/examples/01-web-http-lb.cfg

도우미 스크립트를 쓰면 짧아집니다.

  /usr/share/haproxy/examples/check-example.sh 01-web-http-lb.cfg
  /usr/share/haproxy/examples/check-example.sh --all

03번과 04번은 인증서 파일(/etc/haproxy/certs/example.com.pem)이 실제로 있어야
검사를 통과합니다. 파일 안 주석에 만드는 방법이 적혀 있습니다.

15번은 global 섹션에 external-check 선언이 있어야만 검사가 됩니다. 예제와 이름이
같은 .global 파일이 있으면 check-example.sh 가 00-base.cfg 대신 그것을 뼈대로
골라 쓰므로, 따로 해 줄 일은 없습니다.

recipe- 세트도 같은 방법으로 검사할 수 있습니다.

  /usr/share/haproxy/examples/check-example.sh recipe-05-basic-auth.cfg

다만 recipe-02 는 인증서가, recipe-12 는 맵 파일이 미리 있어야 합니다.
파일 안 주석에 준비 방법이 적혀 있습니다.

  touch /etc/haproxy/blocked.map

------------------------------------------------------------------------------
 주의
------------------------------------------------------------------------------

* 예제를 여러 개 붙여 넣을 때는 이름과 포트가 겹치지 않는지 확인하세요.
  여러 예제가 frontend web / backend web_servers 라는 같은 이름과 :80 포트를
  쓰고 있습니다. 겹치면 HAProxy가 시작되지 않습니다.

* defaults 는 자기 뒤에 나오는 섹션에만 적용됩니다. 예제는 항상 설정 파일
  "끝"에 붙여 넣으세요.

* 10.0.0.x 는 모두 예시 주소입니다. 그대로 두면 모든 서버가 DOWN으로 뜹니다.

* 이 디렉터리의 파일은 패키지를 업그레이드하면 최신 내용으로 교체됩니다.
  직접 고쳐 쓸 내용은 다른 곳에 복사해 두세요.

------------------------------------------------------------------------------
 더 읽을 것
------------------------------------------------------------------------------

  /usr/share/doc/haproxy/configuration.txt   전체 설정 문법 레퍼런스
  /usr/share/doc/haproxy/intro.txt           HAProxy 입문 문서
  /usr/share/doc/haproxy/management.txt      관리 소켓·명령 레퍼런스
  https://docs.haproxy.org/                  온라인 공식 문서
