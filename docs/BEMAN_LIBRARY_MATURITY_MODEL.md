---
sidebar_position: 5
---

import beman_library_production_ready_api_may_undergo_changes from '../images/logos/beman_logo-beman_library_production_ready_api_may_undergo_changes.png'
import beman_library_under_development from '../images/logos/beman_logo-beman_library_under_development.png'
import beman_library_retired from '../images/logos/beman_logo-beman_library_retired.png'
import beman_library_production_ready_stable_api from '../images/logos/beman_logo-beman_library_production_ready_stable_api.png'

# The Beman Library Maturity Model

<!--
SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
-->

`The Beman maturity model` helps developers quickly assess the production readiness of Beman libraries by classifying them based on development phase and interface stability.


![Beman Flow Model](../images/beman_flow-beman_library_maturity_model.png)

### Under development and not yet ready for production use.
<img src={beman_library_under_development} style={{ width: '5%', height: 'auto' }} alt="Beman Library Under Development" /> These libraries may deviate from the Beman Standard due to incompleteness, lack of testing, inconsistencies with the specification, or other non-conformances.

> They are not recommended for production usage!

### Production ready. API may undergo changes.
<img src={beman_library_production_ready_api_may_undergo_changes} style={{ width: '5%', height: 'auto' }} alt="Beman Library Production Ready API May Undergo Changes" /> These Beman-compliant libraries are production-ready, fully implementing the target paper with complete testing and documentation. Users should be aware that future API changes are possible and that standardization is not guaranteed.

> These libraries are recommended for production usage.

### Production ready. Stable API.
<img src={beman_library_production_ready_stable_api} style={{ width: '5%', height: 'auto' }} alt="Beman Library Production Ready Stable API" /> These production-ready libraries offer stable, standardized APIs. They are part of the C++ Standard and can be used as a polyfill for compilers lacking native support. Note that these libraries will be retired after two standardization cycles (6 years).

> These libraries are recommended for production usage.

### Retired. No longer maintained or actively developed.
<img src={beman_library_retired} style={{ width: '5%', height: 'auto' }} alt="Beman Library Retired" /> These libraries were archived and no longer maintained. These libraries are not recommended for production use.

> These libraries are not recommended for production use!
> These libraries were removed from the Beman main distribution, but the initial authors could still support them outside the Beman Project.

Transition examples:

* They were [Production ready. Stable API.](./BEMAN_LIBRARY_MATURITY_MODEL.md#production-ready-stable-api) at some point, but are no longer developed or maintained, being superseded by native compiler implementations - `Mature retirement`.

* They were [Production ready. API may undergo changes.](./BEMAN_LIBRARY_MATURITY_MODEL.md#production-ready-api-may-undergo-changes) at some point, but are no longer developed or maintained, being rejected from the ISO C+ Standardization - `Early retirement`.

* They were [Under development and not yet ready for production use.](./BEMAN_LIBRARY_MATURITY_MODEL.md#under-development-and-not-yet-ready-for-production-use) at some point and were abandoned - `Early retirement`.
