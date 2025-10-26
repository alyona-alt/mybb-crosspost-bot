function decodeEntities(str) {
  if (!str || typeof str !== "string") return "";
  return str.replace(/&amp;/g, "&");
}

function isAdRelated(text) {
  const patterns = [
    /реклам/i,
    /реклама/i,
    /\bвзаимная\s+реклама\b/i,
    /реклама\s*#?\d+/i,
    /реклама\s*\/\/\s*\d+/i,
    /ваша\s+реклама/i,
    /наша\s+реклама/i,
    /рекламные\s+листовки/i,
    /листовки/i,
    /банерообмен/i
  ];
  return patterns.some(p => p.test(text));
}

function checkForNewAdTopicsUnified() {
  const ss = SpreadsheetApp.openById("1jxbsJM2oJiVXUqJmGBFgyZ409tf9LQeW3mYzmk0sZPQ");
  const sheet = ss.getSheetByName("automatic список тем для рекламы (05.25)");
  const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 7).getValues();

  const keywords = ["реклама", "ваша", "наша", "листовки", "pr", "пиар", "пыль"];
  const excludeWords = ["партнеры", "партнёрство", "partners", "реклама от игроков", "пиар от"];
  const domainRegex = /^(https?:\/\/[^\/]+)/;
  const topicRegex = /viewtopic\.php\?id=(\d+)/;

  for (let i = 0; i < data.length; i++) {
    const [originalLink, domainCell] = data[i];
    Logger.log(`▶ Строка ${i + 2}`);
    Logger.log(`🔗 A: ${originalLink}`);

    if (!originalLink || !originalLink.startsWith("http")) continue;

    const domainMatch = originalLink.match(domainRegex);
    const originalIdMatch = originalLink.match(topicRegex);
    if (!domainMatch || !originalIdMatch) continue;

    const domain = domainMatch[1];
    const originalId = originalIdMatch ? parseInt(originalIdMatch[1], 10) : null;

    const targetPage = domain + "/";

    let fallbackLink = null;
    let lastAdVisibleText = null;
    let lastAdLink = null;

    try {
      const response = UrlFetchApp.fetch(targetPage, { muteHttpExceptions: true });

      let html;
      try {
        html = Utilities.newBlob(response.getContent()).getDataAsString("Windows-1251");
        Logger.log("📦 Кодировка: Windows-1251 успешно применена");
      } catch (e) {
        html = response.getContentText();
        Logger.log("⚠️ Использую UTF-8 (Windows-1251 не сработала)");
      }

      const trBlocks = [...html.matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/gi)];

      for (const tr of trBlocks) {
        const trHtml = tr[0].toLowerCase();
        let visibleText = trHtml.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

        let fixedText;
        try {
          fixedText = decodeURIComponent(escape(visibleText));
        } catch (e) {
          fixedText = visibleText;
        }

        const matched = isAdRelated(visibleText) || isAdRelated(fixedText);
        if (!matched) continue;
        if (excludeWords.some(ex => visibleText.includes(ex) || fixedText.includes(ex))) continue;

        lastAdVisibleText = visibleText;

        const linkMatch = trHtml.match(/<a[^>]+class=["']lastpost-link["'][^>]*href=["']([^"']+)["']/i);
        if (linkMatch) {
          const rawHref = decodeEntities(linkMatch[1]);
          const topicMatch = rawHref.match(topicRegex);
          if (!topicMatch) continue;

          const newId = parseInt(topicMatch[1], 10);
          const fullLink = domain + "/viewtopic.php?id=" + newId;
          lastAdLink = fullLink;

          if (newId > originalId) {
            Logger.log(`🟢 Новая тема! ID ${newId} > ${originalId}`);
            sheet.getRange(i + 2, 3).setValue(fullLink);
            sheet.getRange(i + 2, 4).setValue("🟢 появилась новая тема!");
            sheet.getRange(i + 2, 5).setValue("ключ: реклама");
            sheet.getRange(i + 2, 1, 1, 7).setBackground("#d4edda");
            break;
          } else {
            fallbackLink = fullLink;
            Logger.log(`ℹ️ Нашли, но ID старый: ${newId}`);
          }
        }
      }

      const existingC = sheet.getRange(i + 2, 3).getValue();
      // ✅ Всегда вставляем в F последнюю найденную рекламную ссылку
      if (fallbackLink) {
        Logger.log(`🔗 F: записываю ссылку ${fallbackLink}`);
        sheet.getRange(i + 2, 6).setValue(fallbackLink);
      }


      if (!domainCell || domainCell.toString().trim() === "") {
        sheet.getRange(i + 2, 2).setValue(domain);
      }

      if (lastAdVisibleText) {
        sheet.getRange(i + 2, 7).setValue(lastAdVisibleText); // G — текст рекламы
        Logger.log(`📝 G: ${lastAdVisibleText}`);
      }

      if (lastAdLink) {
        sheet.getRange(i + 2, 6).setValue(lastAdLink); // F — найденная последняя ссылка
        Logger.log(`🔗 F: ${lastAdLink}`);
      }

    } catch (e) {
      Logger.log(`❌ Ошибка у ${originalLink}: ${e}`);
      sheet.getRange(i + 2, 3).setValue("❌ ошибка загрузки");
    }
  }


//  Logger.log(`📌 ID из A (original): ${originalId}`);
//  Logger.log(`📌 ID новой темы (найденной): ${newId}`);
//  Logger.log("✅ Готово");
}
S
