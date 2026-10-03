// Synthetic fixture: display-only band.
import type { Register } from 'claude-code'

export const register: Register = (on) => {
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const { Text } = $.ui.resolve(e)
    const usage = await $.session.usage()
    return Text({ children: `context ${usage.context?.percent ?? 0}%` })
  })
}
