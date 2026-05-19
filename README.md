# sc2-replay-slack-bot

Google Drive로 동기화되는 StarCraft II 리플레이 폴더를 macOS에서 1분마다 스캔하고, 새 `.SC2Replay` 파일이 생기면 `sc2reader`로 메타데이터를 읽은 뒤 LLM 분석 결과를 Slack webhook으로 보내는 앱입니다.

## 동작 방식
1. Windows의 StarCraft II 리플레이 폴더를 Google Drive와 동기화합니다.
2. Mac에서도 같은 Google Drive 폴더를 내려받아 로컬 경로로 노출합니다.
3. 이 프로젝트의 launchd 작업이 60초마다 해당 폴더를 스캔합니다.
4. 새 파일 또는 내용이 바뀐 파일만 SHA-256으로 감지합니다.
5. `sc2reader`로 리플레이 메타데이터를 추출합니다.
6. 프로토스/저그/테란 가이드 요약 문서를 prompt context로 함께 넣어 LLM 분석을 생성합니다.
7. 결과를 Slack incoming webhook으로 전송합니다.

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
  llm.py            # OpenAI-compatible LLM 호출
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
LLM_API_KEY=...실제 API 키...
LLM_MODEL=gpt-4.1-mini
LLM_API_BASE_URL=https://api.openai.com/v1
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
- 기본 구현은 `sc2reader` 메타데이터 중심입니다. 세부 전투 이벤트, 빌드 타이밍, 멀티 타이밍, 유닛 손실 곡선 같은 고급 분석은 후속 확장 포인트입니다.
- LLM API 키가 없으면 로컬 fallback 텍스트 요약으로 동작합니다.
- 실제 샘플 리플레이가 저장된 경로만 연결되면 바로 검증 가능합니다.
