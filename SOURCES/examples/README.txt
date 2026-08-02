HAProxy 설정 예제 모음
===========================================================================

이 디렉터리의 파일은 바로 쓸 수 있는 설정 조각입니다.
필요한 것을 골라 /etc/haproxy/haproxy.cfg 끝에 붙여 넣고
IP 주소와 포트만 환경에 맞게 고치면 됩니다.

  01-web-http.cfg          웹 서버 부하 분산 (HTTP), 헬스체크 조정
  02-https.cfg             HTTPS 처리(SSL 종료), HTTP→HTTPS 전환, HTTP/2
  03-routing.cfg           경로·도메인별 라우팅 (ACL)
  04-sticky-session.cfg    세션 고정 (쿠키 / 접속자 IP)
  05-basic-auth.cfg        HTTP 기본 인증
  06-mysql.cfg             MySQL/MariaDB (읽기·쓰기 분리 포함)
  07-postgresql.cfg        PostgreSQL
  08-redis.cfg             Redis (마스터 자동 판별)
  09-tcp.cfg               일반 TCP 서비스 중계
  10-rate-limit.cfg        접속 제한과 속도 제한
  11-maintenance.cfg       서버 점검 처리
  12-dynamic-exclusion.cfg 외부 정보로 서버를 동적으로 제외


적용하는 방법
---------------------------------------------------------------------------

  1. 백업
     cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak

  2. 예제를 붙여 넣고 IP 수정
     vi /etc/haproxy/haproxy.cfg

  3. 검사한 뒤 반영
     haproxy -c -f /etc/haproxy/haproxy.cfg && systemctl reload haproxy

3번에서 && 로 이어 둔 것이 중요합니다. 문법 검사가 실패하면 리로드가
실행되지 않으므로, 잘못된 설정이 서비스에 반영되는 사고를 막아 줍니다.


붙여 넣기 전에 미리 시험해 보기
---------------------------------------------------------------------------

파일을 고치지 않고도 예제가 현재 설정과 잘 맞는지 확인할 수 있습니다.
-f 를 여러 번 주면 HAProxy 가 설정을 합쳐서 검사합니다.

  haproxy -c -f /etc/haproxy/haproxy.cfg -f 01-web-http.cfg


주의할 점
---------------------------------------------------------------------------

* 예제는 한 번에 하나씩 적용하세요. 여러 개를 동시에 붙여 넣으면
  같은 포트(:80)를 두 번 쓰게 되어 기동에 실패합니다.

* 02-https.cfg 는 인증서 파일이 실제로 있어야 검사를 통과합니다.

* 프록시 이름(web, web_servers 등)이 기존 설정과 겹치면 안 됩니다.
  겹치면 알아보기 쉬운 다른 이름으로 바꿔 주세요.

* 모든 예제는 HAProxy 3.4.3 에서 문법 검사를 통과하는 것을 확인했습니다.


더 읽을거리
---------------------------------------------------------------------------

  설정 매뉴얼   https://docs.haproxy.org/3.4/configuration.html
  운영 가이드   https://docs.haproxy.org/3.4/management.html
  man haproxy
