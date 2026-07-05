package cli

import (
	"fmt"
	"os"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// runWithSpinner は task を実行し、TTY かつ色付き可能なときはスピナーを表示する。
// 非 TTY(パイプ/CI)では素朴に task を実行し、TUI を出さない(ログを汚さない)。
// task の戻り値のエラーをそのまま返す。
func runWithSpinner(label string, task func() error) error {
	if !isInteractive() || !colorEnabled(os.Stderr) {
		return task()
	}

	m := spinnerModel{spinner: newSpinner(), label: label}
	p := tea.NewProgram(m, tea.WithOutput(os.Stderr))

	// 変換は同期的でキャンセル不可なため、別 goroutine で走らせ完了を通知する。
	go func() {
		err := task()
		p.Send(taskDoneMsg{err: err})
	}()

	final, runErr := p.Run()
	if runErr != nil {
		// TUI 起動に失敗した場合でも、task の結果を取りこぼさないよう待ち直す。
		return task()
	}
	return final.(spinnerModel).err
}

// newSpinner は控えめな配色のドットスピナーを返す。
func newSpinner() spinner.Model {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("36")) // cyan
	return s
}

// taskDoneMsg は task 完了(結果付き)を伝える bubbletea メッセージ。
type taskDoneMsg struct{ err error }

// spinnerModel は「作業中スピナー + ラベル」だけの最小 bubbletea モデル。
type spinnerModel struct {
	spinner  spinner.Model
	label    string
	quitting bool
	err      error
}

func (m spinnerModel) Init() tea.Cmd { return m.spinner.Tick }

func (m spinnerModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case taskDoneMsg:
		m.err = msg.err
		m.quitting = true
		return m, tea.Quit
	case tea.KeyMsg:
		if msg.Type == tea.KeyCtrlC {
			m.quitting = true
			return m, tea.Quit
		}
		return m, nil
	default:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	}
}

func (m spinnerModel) View() string {
	if m.quitting {
		return ""
	}
	return fmt.Sprintf(" %s %s", m.spinner.View(), m.label)
}
