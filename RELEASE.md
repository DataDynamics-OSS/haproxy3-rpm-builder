# 버전별 주요 기능 및 개선사항

이 저장소가 패키징하는 HAProxy 각 버전에 어떤 기능이 들어왔는지 정리한 문서입니다. 업그레이드를 검토하거나 새로 구축할 버전을 고를 때 참고하세요.

패키지 내려받기는 [Releases](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases) 에서 하시면 됩니다. 설치·설정 방법은 [README](README.md) 를 보세요.

---

## 어떤 버전을 선택해야 하나요

| 버전 | 릴리스 | 지원 종료 | 상태 | 권장 대상 |
|---|---|---|---|---|
| **3.4** | 2026-06-03 | 2031년 2분기 | **LTS** | **신규 구축에 권장.** 지원 기간이 가장 길고 기능도 가장 많습니다. |
| 3.3 | 2025-11-26 | 2027년 1분기 | 일반 안정 | 최신 기능이 급히 필요한 경우. 지원이 1년 남짓이라 장기 운영에는 부적합합니다. |
| 3.2 | 2025-05-28 | 2030년 2분기 | LTS | 이미 3.2로 운영 중이라면 계속 써도 좋습니다. |
| 3.1 | 2024-11-26 | **종료됨** | ⚠️ 지원 종료 | **신규 사용 금지.** 보안 수정이 더 이상 나오지 않습니다. |
| 3.0 | 2024-05-29 | 2029년 2분기 | LTS | 이미 3.0으로 운영 중인 환경의 유지보수용. |

**고민된다면 3.4를 쓰세요.** LTS라 2031년까지 보안 수정이 나오고, 아래 정리한 기능이 모두 들어 있습니다.

이미 운영 중이라면 굳이 최신으로 옮길 필요는 없습니다. **3.0과 3.2도 LTS**라 각각 2029년, 2030년까지 지원됩니다. 다만 **3.1은 이미 지원이 끝났으므로** 쓰고 계시다면 3.2 이상으로 옮기시기를 권합니다.

---

## 업그레이드 전에 알아 둘 것

### ⚠️ 3.3부터 기본 부하분산 알고리즘이 바뀌었습니다

`backend` 에 `balance` 를 적지 않았을 때 적용되는 기본값이 **`roundrobin` 에서 `random` 으로 바뀌었습니다.** 3.2 이하에서 3.3 이상으로 올릴 때 **설정을 그대로 두면 트래픽 분배 방식이 달라집니다.**

`random` 은 후보 두 대를 무작위로 뽑아 연결이 적은 쪽을 고르는 방식(Power-of-Two Choices)이라 대체로 더 고르게 분산되지만, **순서대로 도는 동작에 의존하는 환경이라면 예상과 다르게 보일 수 있습니다.** 기존 동작을 유지하려면 명시적으로 적어 주세요.

```
backend web_servers
  balance roundrobin      # 기본값에 의존하지 말고 명시
  server web1 10.0.0.11:8080 check
```

기본값에 의존하지 말고 **항상 명시하는 편**이 버전을 올릴 때 안전합니다.

### 구버전 패키지에도 최신 기능이 일부 들어 있습니다

HAProxy는 유지보수 중인 브랜치에 위험이 낮은 기능을 **백포트**하기도 합니다. 그래서 "3.4 신규 기능"이 3.0이나 3.2의 최신 패치 버전에도 들어 있는 경우가 있습니다.

이 저장소가 배포하는 패키지에서 실제로 확인된 예는 다음과 같습니다.

| 기능 | 최초 도입 | 3.0.26 | 3.2.22 | 3.3.13 |
|---|---|---|---|---|
| TLS 인증서 압축 (`tune.ssl.certificate-compression`) | 3.4 | 있음 | 있음 | 있음 |
| ACME DNS-01 / EAB | 3.3 / 3.4 | 없음 | 있음 | 있음 |

즉 **각 브랜치의 최신 패치를 쓰는 것만으로도** 일부 신기능을 얻을 수 있습니다. 반대로 말하면 "이 기능을 쓰려면 3.4로 올려야 한다"고 단정하기 전에, 지금 쓰는 브랜치의 최신 버전 문서(`man haproxy` 또는 `/usr/share/doc/haproxy/configuration.txt`)를 먼저 확인해 보시는 편이 좋습니다.

---

## HAProxy 3.4 — 최신 LTS

> 2026-06-03 릴리스 · 2031년 2분기까지 지원 · [패키지 받기](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases/tag/v3.4.7)

운영 편의성이 가장 크게 개선된 릴리스입니다. **재시작 없이 백엔드를 통째로 추가·삭제**할 수 있게 된 것이 핵심이고, 관측(OpenTelemetry)과 암호화 관련 기능도 대폭 늘었습니다.

### 동적 백엔드 — 재시작 없는 배포

프로젝트 역사상 가장 많이 요청된 기능입니다. 이전에는 백엔드를 하나 추가하려면 설정 파일을 고치고 리로드해야 했지만, 이제 **런타임 API만으로 백엔드를 만들고, 서버를 넣고, 공개하고, 지울 수 있습니다.** 서비스가 자주 추가·삭제되는 환경이라면 리로드 자체를 없앨 수 있습니다.

### OpenTelemetry 지원

`filter opentelemetry` 로 분산 추적을 붙일 수 있습니다. 어떤 이벤트를 수집하고 어디로 보낼지는 별도 설정 파일로 지정합니다.

> 기존 OpenTracing 연동은 **폐기 예정**이며 **3.5에서 제거**됩니다. OpenTracing을 쓰고 계신다면 이번 기회에 OpenTelemetry로 옮기세요.

### 그 밖의 주요 기능

| 기능 | 설명 |
|---|---|
| `healthcheck` 섹션 | 헬스체크 설정을 한 번 정의해 여러 백엔드에서 재사용 |
| JWT 복호화 | `jwt_decrypt_cert` · `jwt_decrypt_secret` · `jwt_decrypt_jwk` 컨버터 |
| AES-CBC 암복호화 | `aes_cbc_enc` · `aes_cbc_dec` 컨버터 |
| ACME 강화 | DNS 챌린지 유지와 EAB(외부 계정 바인딩) 지원 |
| TLS 인증서 압축 | RFC 8879. 전송량이 줄어 지연시간 개선 (구버전에 백포트됨) |
| `filter-sequence` | 필터 실행 순서를 명시적으로 지정 |
| Lua 라이브러리 제어 | `tune.lua.openlibs` 로 로드할 표준 라이브러리 선택 |
| HTTP/1 glitch 탐지 | 기존 HTTP/2·QUIC에 더해 HTTP/1도 이상 동작 시 연결을 정상 종료 |
| TLS 디버깅 | keylog 파일 생성용 변수 제공으로 패킷 복호화가 쉬워짐 |
| 성능 | 코어가 많은 CPU에서 요청 처리율 최대 20% 향상, 버퍼 할당 개선 |

---

## HAProxy 3.3

> 2025-11-26 릴리스 · 2027년 1분기까지 지원 · [패키지 받기](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases/tag/v3.3.13)

암호화 성능과 통계 유지에 초점이 맞춰진 릴리스입니다. **기본 부하분산 알고리즘이 바뀐 버전**이므로 [업그레이드 전에 알아 둘 것](#업그레이드-전에-알아-둘-것)을 꼭 확인하세요.

### 커널 TLS (kTLS)

TLS 핸드셰이크 이후의 대칭키 암복호화를 **리눅스 커널에 넘깁니다.** 사용자 공간과 커널 사이의 데이터 복사가 줄어 대용량 전송에서 CPU 사용량이 내려갑니다.

### 통계 유지 (persistent stats)

프론트엔드·백엔드·서버 통계를 공유 메모리에 저장해 **리로드해도 수치가 초기화되지 않습니다.** 설정을 자주 바꾸는 환경에서 그래프가 끊기던 문제가 해소됩니다. `show stat` 결과에 휘발성(V)/영구(P) 표시가 붙습니다.

### 그 밖의 주요 기능

| 기능 | 설명 |
|---|---|
| ACME DNS-01 | DNS TXT 레코드로 도메인 검증. 80포트를 열 수 없는 환경에서 유용 |
| 자동 SNI | HTTP Host 헤더에서 서버 측 SNI를 자동 설정 |
| `ssl-passphrase-cmd` | 암호가 걸린 개인키를 외부 명령으로 해제 |
| `tcp-md5sig` | TCP MD5 서명 지원 (BGP 세션 보호) |
| `jwt_verify_cert` | X.509 인증서에서 공개키를 직접 추출해 JWT 검증 |
| ECH (실험적) | ClientHello 자체를 암호화하는 `ech` bind 인자 |
| HTTP/3 백엔드 (실험적) | `quic4@` 로 백엔드 연결에도 QUIC 사용 |
| CPU 정책 기본값 | 이기종 CPU에서 성능 코어를 우선 사용 |
| `abortonclose` 기본 활성 | 클라이언트가 끊은 요청을 백엔드가 계속 처리하지 않음 |

---

## HAProxy 3.2 — LTS

> 2025-05-28 릴리스 · 2030년 2분기까지 지원 · [패키지 받기](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases/tag/v3.2.22)

**인증서 자동 발급(ACME)이 처음 들어온 버전**이자, 부하분산 알고리즘 성능이 크게 좋아진 릴리스입니다.

### ACME — 인증서 자동 발급

Let's Encrypt나 ZeroSSL에서 인증서를 **HAProxy가 직접 발급받고 갱신**합니다. certbot 같은 외부 도구 없이 만료 7일 전에 자동으로 갱신됩니다. 처음에는 HTTP-01 챌린지만 지원했고, DNS-01은 3.3에서 추가됐습니다.

### 부하분산 성능 향상

`leastconn` 이 **60~260%**, `roundrobin` 이 **150%** 더 잘 확장됩니다. 서버 대수가 많거나 코어 수가 많은 장비일수록 체감이 큽니다.

### 그 밖의 주요 기능

| 기능 | 설명 |
|---|---|
| `cpu-policy` · `cpu-set` | CPU 바인딩 자동화 |
| `ssl-f-use` | `crt-store` 의 인증서를 TLS 속성과 함께 참조 |
| `strict-maxconn` | TCP 연결 수 제한을 HTTP 요청 수와 분리 |
| `hash-preserve-affinity` | 일관성 해시에서 서버가 빠졌을 때의 재배치 제어 |
| `idle-ping` | 유휴 HTTP/2 연결의 생존 확인 |
| `check-reuse-pool` | 헬스체크에 유휴 연결 재사용 |
| `http-request pause` | 요청 처리를 지정 시간만큼 지연 |
| 스레드 한도 확대 | 256/16 → **1024/32** (스레드/스레드 그룹) |
| QUIC | 페이싱 기본 활성화, BBR 정식 지원, OpenSSL 3.5 대응 |
| Lua `patref` | Lua 코드에서 ACL·Map 파일을 동적으로 수정 |

---

## HAProxy 3.1 — ⚠️ 지원 종료

> 2024-11-26 릴리스 · **지원 종료 (마지막 릴리스 2026-03-19)** · [패키지 받기](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases/tag/v3.1.17)

> ⚠️ **이 브랜치는 더 이상 보안 수정이 제공되지 않습니다.** 신규 구축에 사용하지 마시고, 운영 중이라면 3.2 이상으로 옮기세요. 아래 기능은 모두 3.2 이후 버전에도 들어 있습니다.

### 로그 프로파일

요청 처리의 각 단계(accept · request · connect · response · close · error)마다 **다른 로그 형식을 지정**할 수 있습니다. `do-log` 액션과 함께 쓰면 원하는 시점에 원하는 내용만 남길 수 있어 문제 추적이 쉬워집니다.

### HTTP/2 업로드 성능

스트림별 윈도우 크기를 동적으로 조절해 **POST 업로드가 최대 20배 빨라졌습니다.** head-of-line 블로킹도 줄었습니다.

### 그 밖의 주요 기능

| 기능 | 설명 |
|---|---|
| 트레이스 정식 지원 | `h1` · `h2` · `h3` · `quic` · `fcgi` · `peers` 등 서브시스템 디버그 메시지 |
| SPOE 재설계 | mux 구조로 바뀌어 부하분산과 스레드 간 연결 공유 가능 |
| 마스터/워커 개선 | 워커가 설정을 직접 파싱해 리로드 불일치와 FD 누수 감소 |
| `init-state` | 첫 헬스체크가 성공할 때까지 서버를 down으로 유지 |
| `set-retries` | 런타임에 재시도 횟수 조정 |
| httpchk Host 헤더 | 헬스체크에서 Host 헤더를 기본 지원 |

---

## HAProxy 3.0 — LTS

> 2024-05-29 릴리스 · 2029년 2분기까지 지원 · [패키지 받기](https://github.com/DataDynamics/haproxy3-rpm-builder-internal/releases/tag/v3.0.26)

3.x 계열의 시작점입니다. **인증서 관리 방식이 정리되고**, 리로드해도 통계가 유지되는 기반이 마련됐습니다.

### crt-store — 인증서 관리 정리

인증서와 관련 파일(체인, OCSP, 키)을 **한 곳에 정의해 두고 여러 곳에서 참조**하는 방식이 도입됐습니다. 이전처럼 파일 경로를 여기저기 반복해 적을 필요가 없어졌습니다.

### 통계 유지의 시작

`guid` 로 설정 객체에 고유 식별자를 붙이고, `dump stats-file` 과 `stats-file` 로 **리로드 전후의 통계를 이어 붙일 수 있습니다.** 3.3의 공유 메모리 기반 통계 유지는 여기서 출발했습니다.

### 그 밖의 주요 기능

| 기능 | 설명 |
|---|---|
| HTTP/2 glitch 제한 | 프로토콜상 유효하지만 악의적인 요청을 세어 제한 (DoS 완화) |
| JSON / CBOR 로그 | 로그를 구조화된 형식으로 출력 |
| `default-crt` | SNI가 맞지 않을 때 쓸 기본 인증서 지정 |
| 스틱 테이블 성능 | 샤딩된 잠금으로 80스레드 환경에서 약 **6배** 향상 |
| `set-fc-tos` · `set-fc-mark` | 연결에 DSCP/fwmark 표시를 붙여 트래픽 우선순위 제어 |
| UUIDv7 | `uuid` 페치에 버전 지정 가능 |
| `@virt` · `@opt` | 파일 없이 메모리상에서 ACL·Map 관리 |
| `hash-key` | 일관성 해시에 서버 주소/포트 사용 |

---

## 출처

각 버전의 기능 목록은 HAProxy 공식 발표를 기준으로 정리했고, **이 저장소가 실제로 빌드한 패키지의 문서와 소스로 교차 검증**했습니다.

- [Announcing HAProxy 3.4](https://www.haproxy.com/blog/announcing-haproxy-3-4)
- [Announcing HAProxy 3.3](https://www.haproxy.com/blog/announcing-haproxy-3-3)
- [Announcing HAProxy 3.2](https://www.haproxy.com/blog/announcing-haproxy-3-2)
- [Announcing HAProxy 3.1](https://www.haproxy.com/blog/announcing-haproxy-3-1)
- [Announcing HAProxy 3.0](https://www.haproxy.com/blog/announcing-haproxy-3-0)
- [haproxy.org](https://www.haproxy.org/) — 브랜치별 지원 기간

지원 기간은 2026년 8월 기준입니다. 최신 상태는 haproxy.org 첫 화면의 "Latest versions" 표에서 확인하세요.
