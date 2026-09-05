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

async function reachFullStep6(page){
  await reachStep3(page);
  await page.locator('.step[data-step="3"] .next').click();
  await page.locator('.step[data-step="4"] .next').click();
  await page.locator('#skipValues').click();
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('release, identificação profissional e links críticos estão coerentes', async ({ page }) => {
  await expect(page.locator('meta[name="application-version"]')).toHaveAttribute('content', '2.3.1');
  await expect(page.locator('body')).toContainText('Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383');
  await expect(page.locator('a[href="tel:188"]')).toHaveCount(1);
  await expect(page.locator('a[href="tel:+55188"]')).toHaveCount(0);
});

test('áudio N3 e carregador de vídeo permanecem disponíveis e vídeo é opt-in', async ({ page }) => {
  await expect(page.locator('audio source[src^="./audio/rpd1-n3.mp3"]')).toHaveCount(1);
  await expect(page.locator('#videoSlot iframe')).toHaveCount(0);
  await page.locator('#loadVideo').click();
  await expect(page.locator('#videoSlot iframe')).toHaveAttribute('src', /youtube-nocookie\.com/);
});

test('sliders começam como não avaliados e só mudam após interação deliberada', async ({ page }) => {
  await page.locator('#situation').fill('Situação breve.');
  await page.locator('.step[data-step="1"] .next').click();
  await expect(page.locator('#beforeOut')).toHaveText('Não avaliado');
  await page.locator('#before').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#beforeOut')).not.toHaveText('Não avaliado');
});

test('erros obrigatórios expõem estado ARIA e descrição associada', async ({ page }) => {
  await page.locator('.step[data-step="1"] .next').click();
  await expect(page.locator('#situation')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.locator('#situation')).toHaveAttribute('aria-describedby', 'situation-error');
  await expect(page.locator('#situation-error')).not.toBeEmpty();
});

test('barra de progresso tem semântica e acompanha modo essencial', async ({ page }) => {
  await expect(page.locator('#progressCard')).toHaveAttribute('role', 'progressbar');
  await expect(page.locator('#progressCard')).toHaveAttribute('aria-valuemax', '7');
  await page.locator('#modeEssential').check({ force: true });
  await expect(page.locator('#progressCard')).toHaveAttribute('aria-valuemax', '5');
  await expect(page.locator('#progressLabel')).toContainText('Passo 1 de 5');
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
  await page.locator('.quick-choice').filter({ hasText: 'Não sei ainda' }).click();
  await expect(page.locator('#distortion_special_0')).toBeChecked();
  await page.locator('.distortion-explore > summary').click();
  await expect(page.locator('.distortion-explore')).toHaveAttribute('open', '');
  await page.locator('.distortion-select').filter({ hasText: 'Catastrofização' }).click();
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

test('resposta alternativa pode ser explicitamente adiada sem bloquear conclusão', async ({ page }) => {
  await reachFullStep6(page);
  await expect(page.locator('.step[data-step="6"]')).toHaveClass(/is-active/);
  await page.locator('.step[data-step="6"] .next').click();
  await expect(page.locator('#response')).toHaveAttribute('aria-invalid', 'true');
  await page.locator('#responsePending').check();
  await expect(page.locator('#response')).toBeDisabled();
  await page.locator('.step[data-step="6"] .next').click();
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
});

test('edição pela síntese volta diretamente à síntese', async ({ page }) => {
  await reachEssentialSummary(page);
  await page.locator('#summary .edit-step').first().click();
  await expect(page.locator('#editReturnBar')).toBeVisible();
  await page.locator('#situation').fill('Situação atualizada.');
  await page.locator('#returnSummary').click();
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
  await expect(page.locator('#summary')).toContainText('Situação atualizada.');
});

test('rascunho é opt-in, usa chave estável e permanece restrito ao sessionStorage', async ({ page }) => {
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).toBeNull();
  await page.locator('#draftToggle').check();
  await page.locator('#situation').fill('Rascunho deliberado.');
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).not.toBeNull();
  await expect.poll(() => page.evaluate(() => localStorage.length)).toBe(0);
});

test('PDF/print essencial oculta seções do modo completo', async ({ page }) => {
  await page.addInitScript(() => { window.print = () => {}; });
  await reachEssentialSummary(page);
  await page.locator('#printPdf').click();
  await page.locator('#actionConfirm').click();
  await expect(page.locator('.print-essential-only')).not.toHaveAttribute('hidden', '');
  for (const el of await page.locator('.print-full-only').all()) {
    await expect(el).toHaveAttribute('hidden', '');
  }
});

test('política de privacidade corresponde à release e identifica o responsável', async ({ page }) => {
  await page.goto('/privacidade.html');
  await expect(page.locator('body')).toContainText('Transparência · v2.3.1');
  await expect(page.locator('body')).toContainText('sessionStorage');
  await expect(page.locator('body')).toContainText('CRP 04/54.383');
});

for (const width of [320, 360, 390, 430, 768, 1024, 1366, 1440, 1920]) {
  test(`sem overflow horizontal em ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    const metrics = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
    expect(metrics.sw).toBeLessThanOrEqual(metrics.iw + 1);
  });
}

test('em 390px a barra de progresso deixa de ser sticky', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect.poll(() => page.locator('#progressCard').evaluate(el => getComputedStyle(el).position)).toBe('static');
});

test('primeiro Tab expõe o link de salto para navegação por teclado', async ({ page }) => {
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip')).toBeFocused();
});
