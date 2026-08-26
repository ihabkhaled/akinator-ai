# Architecture

Three services: `api`, `worker` and `notifier`.

The `notifier` service consumes the `item.created` topic and delivers webhooks.
It scales independently of the api and holds its own delivery-retry state.

Billing reads item counts through the reporting view - see
[the reporting guide](reporting/guide.md).

## Modules

- `src/items` - item storage and retrieval
- `src/billing` - invoicing
