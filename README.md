# sc2-replay-slack-bot

> **사용자 참여 안내는 `docs/user-onboarding.md`를 먼저 보시면 됩니다.**
>
> 핵심 흐름: **공유 Drive 링크 받기 → 공유 폴더를 내 드라이브에 바로가기 추가 → Finder/파일 탐색기에서 `star2-replay`가 보이는지 확인 → Windows의 스타2 `Multiplayer` 폴더를 Google Drive `star2-replay/내이름폴더`로 연결(`mklink /J`) → Slack에서 분석 결과 받기**

Google Drive로 동기화되는 StarCraft II 리플레이 폴더를 macOS에서 1분마다 스캔하고, 새 `.SC2Replay` 파일이 생기면 `sc2reader`로 메타데이터를 읽은 뒤 분석 결과를 Slack webhook으로 보내는 앱입니다. 기본값은 로컬 `hermes-ask-api`의 `/ask`를 호출하는 `heuristic` 분석 모드입니다.

## 동작 방식
1. Windows의 StarCraft II 리플레이 폴더를 Google Drive와 동기화합니다.
2. Mac에서도 같은 Google Drive 폴더를 내려받아 로컬 경로로 노출합니다.
3. 이 프로젝트의 launchd 작업이 60초마다 해당 폴더를 스캔합니다.
4. 새 파일 또는 내용이 바뀐 파일만 SHA-256으로 감지합니다.
5. `sc2reader`로 리플레이 메타데이터를 추출합니다.
6. 프로토스/저그/테란 가이드 요약 문서를 참고 문맥으로 함께 읽어 분석합니다.
7. `ANALYZER_MODE=manual`이면 앱 내부 규칙 기반 분석을 수행하고, 기본값 `ANALYZER_MODE=heuristic`이면 로컬 `hermes-ask-api`의 `/ask`에 `sc2reader` 메타데이터 + tracker 요약 + 가이드 문맥을 함께 보내 최종 분석을 받습니다.
8. 결과를 Slack incoming webhook으로 전송합니다.

## 중요한 판단
- **Google Drive 연동 자체는 업로드/다운로드를 양방향으로 해줄 가능성이 높지만**, 즉시성/충돌 해결/부분 업로드 타이밍은 Google Drive 동기화 상태에 좌우됩니다.
- 그래서 이 앱은 이벤트 기반 대신 **1분 polling + 해시 기반 중복 방지** 구조로 설계했습니다.
- PDF 전체를 모델의 "memory"로 넣는 개념보다는, **가이드 핵심을 markdown context로 정리해서 프롬프트에 주입**하는 방식이 현실적입니다.

## 프로젝트 구조
```text
src/sc2_replay_slack_bot/
  app.py            # run-once CLI
  config.py         # .env 로드
  finder.py         # .SC2Replay 스캔
  guide_context.py  # guides markdown 묶기
  llm.py            # hermes-ask-api /ask 호출
  manual_analysis.py # manual 모드용 규칙 기반 분석
  parser.py         # sc2reader -> JSON facts
  prompting.py      # 분석 prompt 생성
  replay_store.py   # 해시 기반 중복 방지
  slack.py          # webhook 전송

docs/guides/
  protoss.md
  terran.md
  zerg.md

deploy/launchd/
  com.osori.sc2-replay-slack-bot.plist

scripts/
  run_replay_scan.sh
  install_launchd.sh
```

## 설정
```bash
cp .env.example .env
```

`.env` 예시:
```env
REPLAY_DIR=/Users/osori/Library/CloudStorage/GoogleDrive-.../My Drive/StarCraftII/Replays/Multiplayer
STATE_PATH=/Users/osori/workbench/sc2-replay-slack-bot/state/processed_replays.json
GUIDES_DIR=/Users/osori/workbench/sc2-replay-slack-bot/docs/guides
SLACK_WEBHOOK_URL=...실제 webhook...
ANALYZER_MODE=heuristic
# Optional: only process replays modified on/after this time
MIN_REPLAY_MTIME='2026-05-18 00:00:00'
LLM_MODEL=hermes
LLM_API_BASE_URL=http://127.0.0.1:8787
# Optional: manual 모드가 아니어도 LLM_API_KEY는 사용하지 않습니다.
# LLM_API_KEY=
```

## 설치

```bash
uv sync --group dev
chmod +x scripts/run_replay_scan.sh scripts/install_launchd.sh
```

## 수동 테스트
Slack 전송 없이 dry-run:
```bash
uv run python -m sc2_replay_slack_bot.app --dry-run --max-files 5
```

실전 실행:
```bash
uv run python -m sc2_replay_slack_bot.app --max-files 5
```

## launchd 등록
```bash
./scripts/install_launchd.sh
launchctl print gui/$(id -u)/com.osori.sc2-replay-slack-bot
```

## 로그 확인
```bash
tail -f logs/launchd.log
```

## 테스트
```bash
uv run --group dev pytest tests/ -q
```

## 현재 한계
- 기본 구현은 `sc2reader` 메타데이터와 tracker event 중심입니다. 세부 카메라 이벤트, 전투 구간 클러스터링, 멀티 타이밍 시각화 같은 고급 분석은 후속 확장 포인트입니다.
- 기본값 `heuristic` 모드는 로컬 `hermes-ask-api`를 호출하지만, 근거 데이터 자체는 `sc2reader`와 tracker event에서 추출합니다.
- `manual` 모드를 쓰면 앱 내부 규칙 기반 분석으로만 동작합니다.
- 실제 샘플 리플레이가 저장된 경로만 연결되면 바로 검증 가능합니다.
