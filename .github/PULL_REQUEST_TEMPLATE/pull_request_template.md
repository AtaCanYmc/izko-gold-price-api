## Description

<!-- Concise technical summary of the changes in this PR. -->

## Changes

- 

## Type of Change

- [ ] `feat`: New endpoint, selector, or configuration option
- [ ] `fix`: Bug fix in scraper or API response handling
- [ ] `docs`: Documentation or governance updates
- [ ] `refactor`: Internal code change without behavioral alteration
- [ ] `test`: Test or verification additions
- [ ] `chore`: Build, CI, or dependency updates

## Verification

```bash
python -m py_compile app.py scrape.py
python -c "from scrape import to_float; assert to_float('23.450,75') == 23450.75"
```

## Checklist

- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/).
- [ ] `README.md` and `config.json` reflect any interface changes.
- [ ] All local verification commands and CI checks pass.
