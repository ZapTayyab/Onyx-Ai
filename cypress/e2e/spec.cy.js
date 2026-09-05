describe('SNT AI Application Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads the home / login page successfully', () => {
    cy.contains(/Sign in|Dashboard|SNT AI/i).should('be.visible');
    cy.get('div.md\\:pb-28').click();
    cy.get('#pricing span.absolute').click();
    cy.get('#pricing button.relative').click();
    cy.get('#pricing a.text-white').click();
    cy.get('#firstName').click();
    cy.get('button.w-full').click();
    cy.get('a.bg-slate-900').click();
    cy.get('#capabilities div.lg\\:col-span-2 div.mt-auto').click();
    cy.get('#capabilities div.lg\\:col-span-2 div.mt-auto').click();
    cy.get('#capabilities div:nth-child(2) > div.group > div.items-start > div.flex-1').click();
    cy.get('#capabilities div.sm\\:grid-cols-2 div:nth-child(1) div.group div.items-start div.flex-1 p.leading-relaxed').click();
    cy.get('#capabilities div:nth-child(3) div.mt-auto').click();
    cy.get('#capabilities div:nth-child(4) p.leading-relaxed').click();
    cy.get('#security div:nth-child(8) span.leading-relaxed').click();
    cy.get('#security span:nth-child(4)').click();
    cy.get('#security span:nth-child(3)').click();
    cy.get('#security p.text-slate-500.text-xs').click();
    cy.get('#docs a:nth-child(1) p.mt-1').click();
    cy.get('a[href="/docs/quickstart:-your-first-evaluation-in-5-minutes"] svg.group-hover\\:text-blue-500').click();
    cy.get('a.bg-primary').click();
    cy.get('a.bg-primary').click();
    cy.get('svg.h-4').click();
    cy.get('svg.h-4').click();
    cy.get('svg.h-4').click();
    cy.get('svg.h-4').click();
    cy.get('svg.h-4').click();
    cy.get('a.bg-primary').click();
    cy.get('div.flex').click();
    cy.get('span.text-base').click();
    cy.get('a.bg-indigo-900\\/30').click();
    cy.get('span.text-base').click();
    cy.get('div:nth-child(3) li:nth-child(1) a.transition-colors').click();
    cy.get('button:nth-child(2)').click();
    cy.get('button:nth-child(2)').click();
    cy.get('div.flex-wrap button:nth-child(3)').click();
    cy.get('button:nth-child(4)').click();
    cy.get('button:nth-child(5)').click();
    cy.get('button:nth-child(6)').click();
    cy.get('a[href="/blog/introducing-chaos-injection-for-llm-agents"] h2.font-semibold').click();
    cy.get('a.bg-primary').click();
    cy.get('a.bg-primary').click();
    cy.get('a.bg-primary').click();
    cy.get('html').click();
    cy.get('button.w-full').click();
    cy.get('button.w-full').click();
    cy.get('h1.font-bold').click();
    cy.get('span.text-base').click();
  });

  it('interacts with landing page elements', () => {
    cy.get('body').then(($body) => {
      if ($body.find('#how-it-works').length) {
        cy.get('#how-it-works').scrollIntoView();
      }
    });
  });

  it('allows logging in with dev credentials', () => {
    cy.get('body').then(($body) => {
      if ($body.find('input[type="email"]').length) {
        cy.get('input[type="email"]').clear().type('admin@snt.ai');
        cy.get('input[type="password"]').clear().type('admin');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
      }
    });
  });
});

