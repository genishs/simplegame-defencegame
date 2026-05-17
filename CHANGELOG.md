# Changelog

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며, 버전 관리는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

## [Unreleased]

## [0.1.0] - 2026-05-17 — Phase 1 완료

### Added
- 역사 자료 조사 문서 (`docs/01_history_research.md`)
- 게임 컨셉 브리프 (`docs/02_concept_brief.md`)
- 게임 디자인 문서 (`docs/03_game_design_document.md`)
- 기술 아키텍처 문서 (`docs/04_technical_architecture.md`)
- 형상관리 / 브랜칭·릴리즈 전략 문서 (`docs/05_branching_release_strategy.md`)
- CI / 릴리즈 워크플로 설계 문서 (`docs/06_ci_release_workflow.md`)
- 프로젝트 루트 `README.md` (한국어, Phase 1 기준)
- `CHANGELOG.md` (Keep a Changelog 포맷)
- `.gitignore` (Python / 빌드 / IDE / OS / 시크릿 규칙)
- GitHub 협업 자산
  - `.github/pull_request_template.md`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/CODEOWNERS` (전체 파일 SCM 승인 필요)
- GitHub Actions 워크플로
  - `.github/workflows/ci.yml` (Ubuntu + Windows 매트릭스, lint + pytest, 가드 포함)
  - `.github/workflows/build-windows.yml` (`release/win64/dev` 푸시 시 PyInstaller 빌드 + artifact)
  - `.github/workflows/release-windows.yml` (`release/win64/prd` 푸시 / `v*` 태그 시 빌드 + GitHub Release 자동 생성 + .exe 첨부)
- 브랜치 체계: `main`, `develop`, `release/win64/dev`, `release/win64/prd`

### Notes
- 본 버전은 사전 기획·인프라 단계로, 실행 가능한 게임 코드는 아직 포함하지 않습니다.
- 라이선스는 미정이며 추후 결정합니다.

[Unreleased]: https://github.com/genishs/simplegame-defencegame/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/genishs/simplegame-defencegame/releases/tag/v0.1.0
