# GitHub 開放治理與跨標準社群協作

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): GitHub 開放治理與跨標準社群協作
3. Method:
SBOL Visual 的規格文件本身就放在 GitHub 上做版本控管（https://github.com/SynBioDex/SBOL-visual）——這代表整套標準的每一次修改都是一個 pull request (PR)，每一個未解決的問題都是一個 issue，每一個正式版都對應一個 release tag。想提新 glyph 的人開一個 PR、社群公開審議、通過後就進入下一版；標準的歷史從 2009 的 BBF RFC 16、2015 的 SBOL Visual 1、到本論文的 v2 (2019)，再到規格全文 v2.0 與 v2.1，每一步都可以在 git log 上追。作者也刻意把 SBOL Visual 與相鄰的標準（SBOL 2 資料模型、SBGN、SO、SBO、protein visual language）建立正式對齊，避免各自為政。
為什麼把標準當作開源軟體來維護，比傳統的委員會流程好？因為委員會慢、閉門、決策無跡可循；GitHub 流程則相反——每個提案都在公開 issue 討論、每次表決都留下 comment、每個 release 都有精確的 diff。任何實作者都能翻歷史、看到某條規則為什麼在 v2.1 被改掉，不用等年報公告。作者不只把治理平臺搬上 GitHub，還在論文裡明確呼籲期刊與資助單位把「採用 SBOL Visual」列為出版與補助的推薦實務，並援引 Hillson 等人 2016 年的先例。這樣一手放開讓社群提報、一手拉攏期刊倒逼採用，形成雙保險。
開放標準有兩種常見的失敗模式——一是無社群參與、規則過時後被冷落；二是被少數強勢玩家綁架、演變成派系工具。GitHub 治理處理第一種：公開 issue 降低參與門檻、PR 有明確 best-practice 檢查表可稽查、release 讓新提案可以正式吸收進來，避免僵化。期刊政策倡議處理第二種：一旦論文審稿、資助審查把 SBOL Visual 列為推薦實務，社群就有共同壓力遵循同一版標準，任何試圖分岔的實作都會失去論文發表管道。作者對「開放標準常見失敗」的雙保險設計，讓這套視覺語言有機會避開兩邊都翻車的命運。
4. 工具與材料:
- **GitHub (https://github.com/SynBioDex/SBOL-visual)**: 存放 SBOL Visual 規格文件的版本控管平臺，社群於此提交 issue / PR / release。
- **Pull request (PR)**: GitHub 上提交修改的請求，任何人都能開 PR 提新 glyph 或修規則。
- **Issue**: GitHub 上記錄未解決問題的討論串，是提案與辯論的公開場地。
- **Release**: 標記正式版的版本標籤，讓實作者能引用某一版精確規格。
- **標準演進路徑**: BBF RFC 16 (2009) → SBOL Visual 1 (2015) → v2 (本論文, 2019) → 規格全文 v2.0、v2.1，每一步都可在 git log 上追。
- **期刊政策倡議 (Hillson et al. 2016)**: 呼籲期刊與資助單位把採用 SBOL Visual 列為推薦實務，作為社群採用壓力的槓桿。
- **跨標準對齊**: SBOL Visual 正式與 SBOL 2 資料模型、SBGN、SO、SBO、protein visual language 對齊，避免各自為政。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 標準能持續演化又不失控，把整套規格搬上 GitHub 做開源專案式治理，並呼籲期刊採用政策倡議。這解決了「傳統委員會標準決策封閉、且開放標準常因無採用壓力而僵化」的雙重瓶頸——公開 PR / issue / release 降低社群提報門檻，期刊與資助單位的推薦實務則倒逼採用。這一層是前面所有本體綁定、資料映射、軟體整合能長期同步演進的組織基礎。
