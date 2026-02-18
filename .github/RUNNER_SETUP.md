# Self-Hosted Runner Setup (Koheron Build)

This project builds a full Koheron instrument. The build job requires a self-hosted Linux runner.

## Required runner labels

The workflow targets:

- `self-hosted`
- `linux`
- `x64`
- `koheron`

If the job stays in queue, usually no online runner matches these labels.

## Minimal prerequisites on the runner host

- Ubuntu Linux
- `git`, `make`, `python3`, `zip`, `unzip`
- Docker (if Koheron build uses Docker mode)
- Koheron FPGA toolchain prerequisites (Vivado environment for full bitstream build)

## Register runner

1. In GitHub repo: `Settings -> Actions -> Runners -> New self-hosted runner`.
2. Select Linux x64.
3. Run the shown commands on your build machine.
4. Add custom label `koheron` when configuring the runner.
5. Start runner service and keep it online.

## Verify runner availability

In GitHub UI:

- `Actions -> Runners` must show runner as `Idle` or `Active`.
- Labels must include `koheron`.

## Typical queue causes

- Runner service not running
- Runner machine offline
- Missing label `koheron`
- Runner registered at org level but repo has no access
