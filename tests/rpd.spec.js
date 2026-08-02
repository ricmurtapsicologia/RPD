const { test, expect } = require('@playwright/test');

async function reachStep3(page){
  await page.locator('#situation').fill('Recebi uma mensagem curta e fiquei em dúvida sobre o significado.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('A pessoa deve estar chateada comigo.');
}

async function reachEssentialSummary(page){
  await page.locator('#modeEssential').check({ force: true });
  await page.locator('#situation').fill('Recebi uma mensagem curta.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('Fiz algo errado.');
  await page.locator('.step[data-step="3"] .next').click();
  await page.locator('#action').fill('Esperar alguns minutos e pedir esclarecimento de forma direta.');
  await page.locator('.step[data-step="5"] .next').click();
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('áudio e carregador de vídeo permanecem disponíveis', async ({ page }) => {
  await expect(page.locator('audio source[src="./RPD1.mp3"]')).toHaveCount(1);
  await expect(page.locator('#loadVideo')).toBeVisible();
});

test('sliders começam como não avaliados e só mudam após interação', async ({ page }) => {
  await page.locator('#situation').fill('Situação breve.');
  await page.locator('.step[data-step="1"] .next').click();
  await expect(page.locator('#beforeOut')).toHaveText('Não avaliado');
  await page.locator('#before').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#beforeOut')).not.toHaveText('Não avaliado');
});

test('troca do modo completo para essencial não volta ao início', async ({ page }) => {
  await reachStep3(page);
  await page.locator('.step[data-step="3"] .next').click();
  await expect(page.locator('.step[data-step="4"]')).toHaveClass(/is-active/);
  await page.locator('#modeEssential').check({ force: true });
  await expect(page.locator('.step[data-step="5"]')).toHaveClass(/is-active/);
  await expect(page.locator('#progressLabel')).toContainText('Passo 4 de 5');
});

test('opções de não classificação são exclusivas com distorções específicas', async ({ page }) => {
  await reachStep3(page);
  await page.locator('#distortion_special_0').check({ force: true });
  await expect(page.locator('#distortion_special_0')).toBeChecked();
  await page.locator('#distortion_0').check({ force: true });
  await expect(page.locator('#distortion_0')).toBeChecked();
  await expect(page.locator('#distortion_special_0')).not.toBeChecked();
});

test('modo essencial mostra apenas próximo passo na etapa de ação', async ({ page }) => {
  await page.locator('#modeEssential').check({ force: true });
  await page.locator('#situation').fill('Situação breve.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('Algo vai dar errado.');
  await page.locator('.step[data-step="3"] .next').click();
  await expect(page.locator('#step5Title')).toHaveText('Próximo passo');
  await expect(page.locator('#value').locator('xpath=ancestor::div[contains(@class,"full-mode-only")]')).toBeHidden();
  await expect(page.locator('#actionLabel')).toContainText('Qual pequeno próximo passo é possível agora?');
});

test('edição pela síntese volta diretamente à síntese', async ({ page }) => {
  await reachEssentialSummary(page);
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
  await page.locator('#summary .edit-step').first().click();
  await expect(page.locator('#editReturnBar')).toBeVisible();
  await page.locator('#situation').fill('Situação atualizada.');
  await page.locator('#returnSummary').click();
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
  await expect(page.locator('#summary')).toContainText('Situação atualizada.');
});

test('PDF essencial oculta seções do modo completo', async ({ page }) => {
  await page.addInitScript(() => { window.print = () => {}; });
  await reachEssentialSummary(page);
  await page.locator('#printPdf').click();
  await page.locator('#actionConfirm').click();
  await expect(page.locator('.print-essential-only')).not.toHaveAttribute('hidden', '');
  for (const el of await page.locator('.print-full-only').all()) {
    await expect(el).toHaveAttribute('hidden', '');
  }
});
